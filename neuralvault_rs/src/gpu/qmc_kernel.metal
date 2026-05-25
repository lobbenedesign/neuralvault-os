// core/gpu/qmc_kernel.metal
#include <metal_stdlib>
using namespace metal;

// Helper to generate a scrambled Sobol sample using a thread-specific seed and Leapfrog position
float generate_sobol_owen_sample(uint thread_seed, uint leap_position) {
    uint result = 0;
    uint gray = leap_position ^ (leap_position >> 1); // Gray code indexing for leapfrog position
    
    for (uint bit = 0; bit < 32; ++bit) {
        if ((gray & (1u << bit)) != 0) {
            result ^= 1u << (31u - bit);
        }
    }
    
    // MurmurHash3 finalizer: fully reversible bijection ensuring uniform distribution conservation
    uint scrambled = result ^ thread_seed;
    scrambled ^= scrambled >> 15;
    scrambled = scrambled * 0x85ebca6b;
    scrambled ^= scrambled >> 13;
    scrambled = scrambled * 0xc2b2ae35;
    scrambled ^= scrambled >> 16;
    
    // Scale to [0, 1) float
    return (float)scrambled / 4294967296.0;
}

// Beasley-Springer-Moro inverse normal mapping for high-precision Gaussian mapping
float inverse_normal_transform(float p) {
    p = clamp(p, 0.0001f, 0.9999f);
    float x = p - 0.5f;
    if (abs(x) < 0.42f) {
        float r = x * x;
        return x * (((2.50662823884f * r - 30.8559893949f) * r + 102.837390235f) * r - 116.701525273f) /
               ((((r - 16.5479756484f) * r + 71.5091298651f) * r - 107.131514778f) * r + 20.2737538191f);
    } else {
        float r = (x > 0.0f) ? (1.0f - p) : p;
        float s = sqrt(-log(r));
        float t = (((0.010328f * s + 0.802853f) * s + 2.515517f) /
                  (((0.001308f * s + 0.189269f) * s + 1.432788f) * s + 1.0f)) - s;
        return (x > 0.0f) ? -t : t;
    }
}

kernel void sobol_owen_leapfrog_kernel(
    device float* output_matrix       [[buffer(0)]],
    constant uint& global_seed        [[buffer(1)]],
    constant uint& dimensions         [[buffer(2)]],
    uint2 thread_id                   [[thread_position_in_grid]]
) {
    uint sample_idx = thread_id.x;
    uint dim_idx = thread_id.y;
    
    // Seed unico per thread combinando thread_id e global_seed (MurmurHash-like)
    uint thread_seed = global_seed ^ (sample_idx * 0x9e3779b9) ^ (dim_idx * 0x85ebca6b);
    
    // Algoritmo Leapfrog: calcola lo skip deterministico nella sequenza Sobol
    uint leap_position = sample_idx * dimensions + dim_idx;
    
    float raw_sample = generate_sobol_owen_sample(thread_seed, leap_position);
    
    // Beasley-Springer-Moro inverse normal mapping per convertire in distribuzione Gaussiana
    output_matrix[sample_idx * dimensions + dim_idx] = inverse_normal_transform(raw_sample);
}
