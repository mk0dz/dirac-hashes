# Dirac Hashes

A next-generation cryptographic hash library built for speed, security, and quantum resistance.

## About

Dirac Hashes is a project aimed at developing and testing high-performance cryptographic hash functions that are resistant to quantum computing attacks. This repository contains tools for testing and comparing the performance of Dirac hash algorithms against industry-standard algorithms.

## Features

- Test and compare multiple hash algorithms:
  - Dirac-256
  - Dirac-512
  - SHA-256
  - SHA3-256
  - BLAKE2b
  - BLAKE3
- Measure and compare performance metrics
- Support for various input encodings
- Save and export hash results
- Performance history tracking

## Getting Started

To run the hash testing tool locally:

1. Clone this repository:
   ```
   git clone https://github.com/your-username/dirac-hashes.git
   cd dirac-hashes
   ```

2. Open `index.html` in your browser or set up a local server:
   ```
   # Using Python 3
   python -m http.server
   
   # Using Node.js with live-server
   npx live-server
   ```

3. Navigate to the Hash Testing Tool from the main page

## Project Structure

```
dirac-hashes/
├── index.html                # Main entry point
├── README.md                 # This file
├── frontend/
│   ├── html/
│   │   └── hash-test.html    # Hash testing interface
│   ├── css/
│   │   └── hash-test.css     # Styles for hash testing
│   └── js/
│       └── hash-test.js      # Hash testing functionality
```

## Future Development

- Implementation of Dirac hash algorithms in Rust and WebAssembly
- Integration with Solana blockchain for high-performance verification
- Command-line tools for batch processing
- Integration tests for cryptographic properties

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 