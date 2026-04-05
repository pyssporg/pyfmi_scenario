cmake_minimum_required(VERSION 3.10)


enable_testing()
    
find_package(GTest CONFIG REQUIRED)

add_executable(scenario_tests
    basic_test.cpp
    scenario_test.cpp
)

target_include_directories(scenario_tests
  PUBLIC
    ${CMAKE_SOURCE_DIR}/libs/scenario_fmu/include

  PRIVATE 
)

target_link_libraries(scenario_tests PRIVATE
    scenario
    GTest::gtest
    GTest::gtest_main
    GTest::gmock
    GTest::gmock_main
)

if(SCENARIO_STATIC_GCC_RUNTIME AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_link_options(scenario_tests PRIVATE -static-libstdc++ -static-libgcc)
endif()


# add_test(NAME scenario_tests COMMAND scenario_tests)
add_test(AllTestsInMain scenario_tests)
