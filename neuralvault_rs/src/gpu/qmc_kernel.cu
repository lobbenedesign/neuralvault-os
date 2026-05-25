// core/gpu/qmc_kernel.cu
#include <cuda_runtime.h>
#include <device_launch_parameters.h>
#include <math.h>

// Helper to generate a scrambled Sobol sample using a thread-specific seed and Leapfrog position
__device__ float generate_sobol_owen_sample(unsigned int thread_seed, unsigned int leap_position) {
    unsigned int result = 0;
    unsigned int gray = leap_position ^ (leap_position >> 1); // Gray code indexing for leapfrog position
    
    for (unsigned int bit = 0; bit < 32; ++bit) {
        if ((gray & (1u << bit)) != 0) {
            result ^= 1u << (31u - bit);
        }
    }
    
    // MurmurHash3 finalizer: fully reversible bijection ensuring uniform distribution conservation
    unsigned int scrambled = result ^ thread_seed;
    scrambled ^= scrambled >> 15;
    scrambled = scrambled * 0x85ebca6b;
    scrambled ^= scrambled >> 13;
    scrambled = scrambled * 0xc2b2ae35;
    scrambled ^= scrambled >> 16;
    
    return (float)scrambled / 4294967296.0f;
}

// Beasley-Springer-Moro inverse normal mapping for high-precision Gaussian mapping
__device__ float inverse_normal_transform(float p) {
    if (p < 0.0001f) p = 0.0001f;
    if (p > 0.9999f) p = 0.9999f;
    float x = p - 0.5f;
    if (fabsf(x) < 0.42f) {
        float r = x * x;
        return x * (((2.50662823884f * r - 30.8559893949f) * r + 102.837390235f) * r - 116.701525273f) /
               ((((r - 16.5479756484f) * r + 71.5091298651f) * r - 107.131514778f) * r + 20.2737538191f);
    } else {
        float r = (x > 0.0f) ? (1.0f - p) : p;
        float s = sqrtf(-logf(r));
        float t = (((0.010328f * s + 0.802853f) * s + 2.515517f) /
                  (((0.001308f * s + 0.189269f) * s + 1.432788f) * s + 1.0f)) - s;
        return (x > 0.0f) ? -t : t;
    }
}

extern "C" __global__ void sobol_owen_leapfrog_kernel(
    float* output_matrix,
    unsigned int global_seed,
    unsigned int dimensions,
    unsigned int num_samples
) {
    unsigned int sample_idx = blockIdx.x * blockDim.x + threadIdx.x;
    unsigned int dim_idx = blockIdx.y * blockDim.y + threadIdx.y;
    
    if (sample_idx < num_samples && dim_idx < dimensions) {
        unsigned int thread_seed = global_seed ^ (sample_idx * 0x9e3779b9) ^ (dim_idx * 0x85ebca6b);
        unsigned int leap_position = sample_idx * dimensions + dim_idx;
        
        float raw_sample = generate_sobol_owen_sample(thread_seed, leap_position);
        output_matrix[sample_idx * dimensions + dim_idx] = inverse_normal_transform(raw_sample);
    }
}
