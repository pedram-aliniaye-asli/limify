# Release Guide

This guide explains how new versions of Limify are released.

Limify follows **semantic versioning** and uses Git tags and GitHub Actions to publish packages.

---

## Versioning

Limify follows **Semantic Versioning (SemVer)**.

Version format:

```
MAJOR.MINOR.PATCH
```

Example versions:

```
0.1.0
0.1.1
0.2.0
```

---

## Version Meaning

### MAJOR version

```
X.0.0
```

Incremented when breaking changes are introduced.

Examples:

- removing public APIs
- changing configuration behavior
- changing request context structure

Example:

```
1.0.0
```

---

### MINOR version

```
0.X.0
```

Incremented when new features are added without breaking existing functionality.

Examples:

- new algorithms
- new framework adapters
- new storage adapters

Example:

```
0.2.0
```

---

### PATCH version

```
0.0.X
```

Incremented for bug fixes or small improvements.

Examples:

- fixing algorithm edge cases
- documentation updates
- small performance improvements

Example:

```
0.1.1
```

---

## Pre-1.0 Versions

Before version **1.0.0**, the API may still evolve.

Example:

```
0.1.x
```

During this stage:

- APIs may change
- internal architecture may evolve
- documentation may expand

However, changes will still aim to remain stable whenever possible.

---

## Creating a Release

Releases are created using **Git tags**.

## Automated Publishing

When a tag is pushed, the GitHub Actions workflow is triggered.

The workflow performs the following steps:

1. checks out the repository
2. installs build tools
3. builds the package
4. runs package validation
5. uploads the package to PyPI

This means **publishing happens automatically after tagging**.


## Versioning

Limify follows semantic versioning.

Example:

0.1.0  
0.1.1  
0.2.0  

## Publishing


GitHub Actions publishes the package to PyPI.


## PyPI Package

After the workflow completes successfully, the new version becomes available on PyPI.

Users can install it with:

```
pip install limifyrate
```

To upgrade:

```
pip install --upgrade limifyrate
```
