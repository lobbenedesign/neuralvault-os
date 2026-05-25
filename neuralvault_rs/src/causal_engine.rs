use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::HashMap;

/// [v9.0] Sobol Sequence Generator for Quasi-Monte Carlo simulations.
/// Provides better coverage of the probability space than standard RNG.
pub struct SobolGenerator {
    index: u32,
    direction_numbers: Vec<u32>,
}

impl SobolGenerator {
    pub fn new(dim_capacity: usize) -> Self {
        // Simplified Sobol direction numbers for the first dimension
        // In a full implementation, we would have unique numbers per dimension
        let mut v = vec![0u32; 32];
        for i in 0..32 {
            v[i] = 1 << (31 - i);
        }
        Self { index: 0, direction_numbers: v }
    }

    pub fn next_f32(&mut self) -> f32 {
        self.index += 1;
        let mut result = 0u32;
        let mut i = self.index;
        let mut j = 0;
        
        // Gray code based Sobol generation
        while i > 0 {
            if i & 1 == 1 {
                result ^= self.direction_numbers[j];
            }
            i >>= 1;
            j += 1;
        }
        
        result as f32 / (u32::MAX as f32)
    }
}

pub fn generate_sobol_owen_sample(thread_seed: u32, leap_position: u32) -> f32 {
    let mut result = 0u32;
    let gray = leap_position ^ (leap_position >> 1);
    
    for bit in 0..32 {
        if (gray & (1 << bit)) != 0 {
            result ^= 1 << (31 - bit);
        }
    }
    
    // MurmurHash3 finalizer: fully reversible bijection ensuring uniform distribution conservation
    let mut scrambled = result ^ thread_seed;
    scrambled ^= scrambled >> 15;
    scrambled = scrambled.wrapping_mul(0x85ebca6b);
    scrambled ^= scrambled >> 13;
    scrambled = scrambled.wrapping_mul(0xc2b2ae35);
    scrambled ^= scrambled >> 16;
    
    scrambled as f32 / 4294967296.0
}


/// Simple inverse normal CDF approximation (Beasley-Springer-Moro)
pub fn inverse_normal_cdf(p: f32) -> f32 {
    let p = p.clamp(0.0001, 0.9999);
    let x = p - 0.5;
    if x.abs() < 0.42 {
        let r = x * x;
        x * (((2.50662823884 * r - 30.8559893949) * r + 102.837390235) * r - 116.701525273) /
            ((((r - 16.5479756484) * r + 71.5091298651) * r - 107.131514778) * r + 20.2737538191)
    } else {
        let r = if x > 0.0 { 1.0 - p } else { p };
        let s = (-r.ln()).sqrt();
        let t = (((0.010328 * s + 0.802853) * s + 2.515517) /
                 (((0.001308 * s + 0.189269) * s + 1.432788) * s + 1.0)) - s;
        if x > 0.0 { -t } else { t }
    }
}

#[derive(Clone)]
pub struct RustCausalEdge {
    pub target_id: String,
    pub weight: f32,
}

#[pyfunction]
pub fn run_stochastic_simulation_rs(
    start_node_id: String,
    initial_impact: f32,
    nodes_data: HashMap<String, Vec<(String, f32)>>,
    iterations: usize,
    depth: usize,
    noise_level: f32
) -> PyResult<HashMap<String, (f32, f32, f32)>> {
    // 1. Preparazione Grafo Rust
    let graph: HashMap<String, Vec<RustCausalEdge>> = nodes_data
        .into_iter()
        .map(|(id, edges)| {
            (
                id,
                edges
                    .into_iter()
                    .map(|(target, weight)| RustCausalEdge { target_id: target, weight })
                    .collect(),
            )
        })
        .collect();

    // 2. Esecuzione Parallela Quasi-Monte Carlo (Rayon + Deterministic Owen-Leapfrog Sobol)
    let global_seed = 42u32;
    let results: Vec<HashMap<String, f32>> = (0..iterations)
        .into_par_iter()
        .map(|i| {
            let mut dim_idx = 0u32;
            let mut current_impacts = HashMap::new();
            current_impacts.insert(start_node_id.clone(), initial_impact);

            let mut active_nodes = vec![(start_node_id.clone(), initial_impact)];

            for _ in 0..depth {
                let mut next_nodes = Vec::new();
                for (nid, impact) in active_nodes {
                    if let Some(edges) = graph.get(&nid) {
                        for edge in edges {
                            // Seed unico per thread/dimensione (MurmurHash-like)
                            let thread_seed = global_seed ^ (i as u32 * 0x9e3779b9) ^ (dim_idx * 0x85ebca6b);
                            // Algoritmo Leapfrog: calcola lo skip deterministico
                            let leap_position = (i as u32) * 1000 + dim_idx;
                            
                            let p = generate_sobol_owen_sample(thread_seed, leap_position);
                            let noise = inverse_normal_cdf(p) * noise_level;
                            
                            let weight_with_noise = (edge.weight + noise).clamp(-2.0, 2.0);
                            let transmission = impact * weight_with_noise;
                            
                            let entry = current_impacts.entry(edge.target_id.clone()).or_insert(0.0);
                            *entry += transmission;
                            next_nodes.push((edge.target_id.clone(), transmission));
                            
                            dim_idx += 1;
                        }
                    }
                }
                active_nodes = next_nodes;
                if active_nodes.is_empty() { break; }
            }
            current_impacts
        })
        .collect();

    // 3. Aggregazione Statistica
    let mut stats: HashMap<String, (Vec<f32>, f32)> = HashMap::new();
    for iter_res in results {
        for (id, val) in iter_res {
            stats.entry(id).or_insert((Vec::new(), 0.0)).0.push(val);
        }
    }

    let mut final_stats = HashMap::new();
    for (id, (vals, _)) in stats {
        let count = vals.len() as f32;
        let mean: f32 = vals.iter().sum::<f32>() / count;
        let variance: f32 = vals.iter().map(|v| (v - mean).powi(2)).sum::<f32>() / count;
        let std = variance.sqrt();
        let prob_pos = vals.iter().filter(|&&v| v > 0.0).count() as f32 / count;
        
        final_stats.insert(id, (mean, std, prob_pos));
    }

    Ok(final_stats)
}
