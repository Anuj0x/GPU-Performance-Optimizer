# GPA - GPU Performance Advisor CMake Configuration
cmake_minimum_required(VERSION 3.16)
project(GPA VERSION 2.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type configuration
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose build type" FORCE)
endif()

# Compiler flags
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    add_compile_options(/W4)
endif()

# CUDA support (if needed for future components)
find_package(CUDA QUIET)
if(CUDA_FOUND)
    enable_language(CUDA)
    set(CMAKE_CUDA_STANDARD 14)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)
endif()

# Python bindings (if needed)
find_package(Python3 COMPONENTS Interpreter Development QUIET)

# Installation directories
include(GNUInstallDirs)

# Create Python package
if(Python3_FOUND)
    # Install Python scripts
    install(PROGRAMS
        install.py
        run_benchmarks.py
        DESTINATION ${CMAKE_INSTALL_BINDIR}
    )

    # Install Python package
    install(DIRECTORY
        python/
        DESTINATION ${Python3_SITEARCH}/gpa
        FILES_MATCHING PATTERN "*.py"
    )

    # Install configuration
    install(FILES
        config.yaml
        DESTINATION ${CMAKE_INSTALL_SYSCONFDIR}/gpa
    )
endif()

# Install documentation
install(DIRECTORY
    docs/
    DESTINATION ${CMAKE_INSTALL_DOCDIR}
)

# Install tests
install(DIRECTORY
    tests/
    DESTINATION ${CMAKE_INSTALL_DATADIR}/gpa/tests
)

# Create uninstall target
if(NOT TARGET uninstall)
    configure_file(
        "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
        "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
        IMMEDIATE @ONLY
    )

    add_custom_target(uninstall
        COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake
    )
endif()

# Package configuration
set(CPACK_PACKAGE_NAME "gpa")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "GPU Performance Advisor")
set(CPACK_PACKAGE_VENDOR "Rice University")
set(CPACK_PACKAGE_CONTACT "gpa-dev@rice.edu")

# Debian packaging
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3, python3-pip, python3-numpy, cuda-toolkit")
set(CPACK_DEBIAN_PACKAGE_SECTION "devel")

include(CPack)

# Print configuration summary
message(STATUS "GPA Configuration Summary:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Install prefix: ${CMAKE_INSTALL_PREFIX}")
if(Python3_FOUND)
    message(STATUS "  Python: ${Python3_VERSION}")
    message(STATUS "  Python executable: ${Python3_EXECUTABLE}")
else()
    message(WARNING "  Python: NOT FOUND (Python components will not be installed)")
endif()
if(CUDA_FOUND)
    message(STATUS "  CUDA: ${CUDA_VERSION}")
else()
    message(STATUS "  CUDA: NOT FOUND")
endif()
