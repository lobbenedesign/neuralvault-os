use pyo3::prelude::*;

mod distance;
mod hnsw_core;
pub mod index;
pub mod turboquant;
pub mod causal_engine;
pub mod gpu_qmc;

#[pyclass]
pub struct PyHNSW {
    inner: Box<dyn index::GpuVectorIndex>,
}

#[pymethods]
impl PyHNSW {
    #[new]
    pub fn new(dim: usize, m: usize, ef_construction: usize) -> Self {
        PyHNSW {
            inner: index::VectorIndexFactory::create(
                index::VectorIndexType::Gpu,
                dim,
                m,
                ef_construction,
            ),
        }
    }

    /// Elimina un nodo dal grafo.
    pub fn delete(&mut self, node_id: String) -> bool {
        self.inner.delete(node_id)
    }

    /// Ritorna il numero di nodi indicizzati.
    pub fn __len__(&self) -> usize {
        self.inner.len()
    }

    /// Inserisce un vettore nel grafo.
    pub fn insert(&mut self, node_id: String, vector: Vec<f32>) {
        self.inner.insert(node_id, vector);
    }

    /// Ricerca i top-k vicini.
    pub fn search(
        &self,
        query: Vec<f32>,
        k: usize,
        ef: usize,
    ) -> Vec<(String, f32)> {
        self.inner.search(query, k, ef)
    }

    /// Estrae un campione di archi per visualizzazione.
    pub fn get_edges_sample(&self, max_edges: usize) -> Vec<(String, String)> {
        self.inner.get_edges_sample(max_edges)
    }

    /// Ritorna il numero totale di archi nel grafo.
    pub fn total_edges(&self) -> usize {
        self.inner.total_edges()
    }

    /// Ritorna il livello massimo attuale.
    pub fn max_level(&self) -> i32 {
        self.inner.max_level()
    }

    /// Blocca l'indice nella memoria fisica (Hardware Pinning).
    /// Ottimizzato per NVIDIA Grace (Unified Memory) e Apple Silicon.
    pub fn pin_to_hardware(&self) -> bool {
        self.inner.pin_to_hardware()
    }

    /// Ritorna la dimensione dei vettori.
    pub fn dim(&self) -> usize {
        self.inner.dim()
    }
}

#[pyclass]
pub struct RustTurboQuant {
    inner: turboquant::PolarQuantizer,
}

#[pymethods]
impl RustTurboQuant {
    #[new]
    pub fn new(dim: usize, bits_main: u8) -> Self {
        RustTurboQuant {
            inner: turboquant::PolarQuantizer::new(dim, bits_main),
        }
    }

    pub fn encode(&self, x: Vec<f32>) -> (f32, Vec<u8>) {
        self.inner.encode(&x)
    }

    pub fn unbiased_dot(&self, query: Vec<f32>, radius: f32, angle_indices: Vec<u8>) -> f32 {
        self.inner.unbiased_dot(&query, radius, &angle_indices)
    }
}

/// Il modulo Rust che verrà importato in Python.
#[pymodule]
fn neuralvault_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyHNSW>()?;
    m.add_class::<RustTurboQuant>()?;
    m.add_class::<gpu_qmc::PyGpuQmcDriver>()?;
    m.add_function(wrap_pyfunction!(causal_engine::run_stochastic_simulation_rs, m)?)?;
    Ok(())
}
