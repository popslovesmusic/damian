# Tower Engine GPU Acceleration Boundary and CPU Fallback

This document outlines the strategy for incorporating optional GPU acceleration within the Tower Engine, emphasizing that GPU support is an enhancement, not a requirement. A robust CPU-based fallback mechanism is mandatory to ensure broad compatibility and adherence to the principle that core gameplay must function without dedicated GPU compute.

## Core Principles

*   **GPU Optionality:** GPU acceleration is strictly optional. The engine's core logic and essential functionalities must not depend on the presence or specific capabilities of a GPU.
*   **CPU Fallback:** All rendering, simulation, and procedural generation components must have a functional CPU-based fallback. This ensures the game is playable on systems without a compatible GPU or when GPU acceleration is disabled.
*   **No CUDA Requirement:** To maintain broad hardware compatibility, the engine will not mandate NVIDIA's CUDA technology. Backend choices will favor open standards or multi-vendor solutions.
*   **No GPU Runtime Implementation (Yet):** This patch only declares the capability boundary. No actual GPU runtime implementation or API integration is performed at this stage.
*   **Web Play Support:** The architecture must continue to support web-based play (e.g., via WebGPU or WebGL), indicating a preference for cross-platform GPU APIs.
*   **Open Backend Choices:** The design remains open to various backend technologies (Vulkan, DirectX, OpenGL, WebGPU, SYCL/oneAPI) to avoid vendor lock-in.

## Acceleration Backend Registry (`engine/core/acceleration_backend_registry.json`)

This registry declares the currently supported and planned compute/render acceleration backends for the Tower Engine. It explicitly lists the required CPU backend and various optional GPU technologies.

### Required Backend:

*   **`cpu`**: The default and mandatory backend. All core game systems rely on CPU functionality.

### Optional Backends (Planned/Candidate):

*   **`webgpu`**: Targeted for browser-based rendering and future browser-side compute.
*   **`opengl`**: Considered for desktop rendering and as a general fallback rendering solution.
*   **`vulkan`**: Planned for modern desktop rendering and future high-performance desktop compute.
*   **`directx`**: Specifically for Windows-based rendering.
*   **`sycl_or_oneapi`**: A candidate for future Intel GPU compute.

### Explicitly Not Required:

*   **`cuda`**: NVIDIA-specific compute API is not a mandatory dependency.
*   **`nvidia_only_stack`**: The engine avoids solutions that exclusively tie it to NVIDIA hardware.

## CPU Fallback Policy

The `fallback_policy` defined in the registry reinforces the CPU-first approach:

*   **`cpu_required`**: Confirms that CPU functionality is always available and expected.
*   **`gameplay_must_run_without_gpu_compute`**: Core gameplay mechanics, logic, and essential systems must function correctly without relying on GPU acceleration. Any GPU-accelerated features must have a graceful CPU equivalent or be entirely optional.
*   **`gpu_may_accelerate_but_not_define_core_logic`**: GPU usage is for performance enhancement or visual fidelity, not for implementing fundamental game logic that would break the game if unavailable.
