#!/usr/bin/env python

# Copyright (c) 2012 Leonhard Gruenschloss (leonhard@gruenschloss.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Generate C++ code for evaluating Halton points with Faure-permutations for different bases.

# How many components to generate.
num_dimensions = 256

# Check primality. Not optimized, since it's not performance-critical.
def is_prime(p):
    for i in range(2, p):
        if not p % i:
            return False
    return True

# Init prime number array.
primes = []
candidate = 1
for i in range(num_dimensions):
    while (True):
        candidate += 1
        if (is_prime(candidate)):
            break;
    primes.append(candidate)

print '''// Copyright (c) 2012 Leonhard Gruenschloss (leonhard@gruenschloss.org)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights to
// use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
// of the Software, and to permit persons to whom the Software is furnished to do
// so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// This file is automatically generated.

#ifndef HALTON_SAMPLER_H
#define HALTON_SAMPLER_H

#include <algorithm>
#include <vector>

// Compute points of the Halton sequence with with digit-permutations for different bases.
class Halton_sampler
{
public:
    // Init the permutation arrays using Faure-permutations. Alternatively, init_random can be
    // called before the sampling functionality can be used.
    void init_faure();

    // Init the permutation arrays using randomized permutations. Alternatively, init_faure can be
    // called before the sampling functionality can be used. The client needs to specify a random
    // number generator function object that can be used to generate a random sequence of integers.
    // That is: if f is a random number generator and N is a positive integer, then f(N) will
    // return an integer less than N and greater than or equal to 0.
    template <typename Random_number_generator>
    void init_random(Random_number_generator& rand);

    // Return the number of supported dimensions.
    static unsigned get_num_dimensions() { return %du; }

    // Return the Halton sample for the given dimension (component) and index.
    // The client must have called init_random or init_faure at least once before.
    // dimension must be smaller than the value returned by get_num_dimensions().
    float sample(unsigned dimension, unsigned index) const;

private:
    static unsigned short invert(unsigned short base, unsigned short digits,
        unsigned short index, const std::vector<unsigned short>& perm);

    void init_tables(const std::vector<std::vector<unsigned short> >& perms);
''' % num_dimensions

for i in range(0, num_dimensions):
    print '    float halton%d(unsigned index) const;' % primes[i]

# The following strings will be extended below.
perm_arrays = '' # Permutation arrays.
init_tables = '' # Loops for initializing the permutation arrays.
# Individual implementations for each dimensions.
halton_impl = '''
// Special case: radical inverse in base 2, with direct bit reversal.
inline float Halton_sampler::halton2(unsigned index) const
{
    index = (index << 16) | (index >> 16);
    index = ((index & 0x00ff00ff) << 8) | ((index & 0xff00ff00) >> 8);
    index = ((index & 0x0f0f0f0f) << 4) | ((index & 0xf0f0f0f0) >> 4);
    index = ((index & 0x33333333) << 2) | ((index & 0xcccccccc) >> 2);
    index = ((index & 0x55555555) << 1) | ((index & 0xaaaaaaaa) >> 1);
    union Result
    {
        unsigned u;
        float f;
    } result; // Write reversed bits directly into floating-point mantissa.
    result.u = 0x3f800000u | (index >> 9);
    return result.f - 1.f;
}
'''

for i in range(1, num_dimensions): # Skip base 2.
    base = primes[i]

    # Based on the permutation table size, we process multiple digits at once.
    digits = 1
    pow_base = base
    while pow_base * base <= 500: # Maximum permutation table size.
        pow_base *= base
        digits += 1

    perm_arrays += '    unsigned short m_perm%d[%d];\n' % (base, pow_base)

    max_power = pow_base
    while max_power * pow_base < (1 << 32): # 32-bit unsigned precision
        max_power *= pow_base
    power = max_power / pow_base

    halton_impl += '''
inline float Halton_sampler::halton%d(const unsigned index) const
{
    return (m_perm%d[index %% %du] * %du +
''' % (base, base, pow_base, power)

    init_tables += '''    for (unsigned short i = 0; i < %d; ++i)
        m_perm%d[i] = invert(%d, %d, i, perms[%d]);
''' % (pow_base, base, base, digits, base)

    # Advance to next set of digits.
    div = 1
    while power / pow_base > 1:
        div *= pow_base
        power /= pow_base
        halton_impl += '            m_perm%d[(index / %du) %% %du] * %du +\n' % (base, div, pow_base, power)

    halton_impl += '''            m_perm%d[(index / %du) %% %du]) * float(0x1.fffffcp-1 / %du); // Results in [0,1).
}
''' % (base, div * pow_base, pow_base, max_power)

print '\n' + perm_arrays + '};'

print '''
inline void Halton_sampler::init_faure()
{
    const unsigned max_base = %du;
    std::vector<std::vector<unsigned short> > perms(max_base + 1);
    for (unsigned k = 1; k <= 3; ++k) // Keep identity permutations for base 1, 2, 3.
    {
        perms[k].resize(k);
        for (unsigned i = 0; i < k; ++i)
            perms[k][i] = i;
    }
    for (unsigned base = 4; base <= max_base; ++base)
    {
        perms[base].resize(base);
        const unsigned b = base / 2;
        if (base & 1) // odd
        {
            for (unsigned i = 0; i < base - 1; ++i)
                perms[base][i + (i >= b)] = perms[base - 1][i] + (perms[base - 1][i] >= b);
            perms[base][b] = b;
        }
        else // even
        {
            for (unsigned i = 0; i < b; ++i)
            {
                perms[base][i] = 2 * perms[b][i];
                perms[base][b + i] = 2 * perms[b][i] + 1;
            }
        }
    }
    init_tables(perms);
}

template <typename Random_number_generator>
void Halton_sampler::init_random(Random_number_generator& rand)
{
    const unsigned max_base = %du;
    std::vector<std::vector<unsigned short> > perms(max_base + 1);
    for (unsigned k = 1; k <= 3; ++k) // Keep identity permutations for base 1, 2, 3.
    {
        perms[k].resize(k);
        for (unsigned i = 0; i < k; ++i)
            perms[k][i] = i;
    }
    for (unsigned base = 4; base <= max_base; ++base)
    {
        perms[base].resize(base);
        for (unsigned i = 0; i < base; ++i)
            perms[base][i] = i;
        std::random_shuffle(perms[base].begin(), perms[base].end(), rand);
    }
    init_tables(perms);
}

inline float Halton_sampler::sample(const unsigned dimension, const unsigned index) const
{
    switch (dimension)
    {''' % (primes[-1], primes[-1])

for i in range(num_dimensions):
    print '        case %d: return halton%d(index);' % (i, primes[i])

print '''    }
    return 0.f;
}

inline unsigned short Halton_sampler::invert(const unsigned short base, const unsigned short digits,
    unsigned short index, const std::vector<unsigned short>& perm)
{
    unsigned short result = 0;
    for (unsigned short i = 0; i < digits; ++i)
    {
        result = result * base + perm[index % base];
        index /= base;
    }
    return result;
}

inline void Halton_sampler::init_tables(const std::vector<std::vector<unsigned short> >& perms)
{'''

print init_tables + '}'

print halton_impl

print '#endif // HALTON_SAMPLER_H\n'

