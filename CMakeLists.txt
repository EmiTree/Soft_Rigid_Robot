# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(Soft_Rigid_Robot C CXX ASM)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. 
add_executable(Soft_Rigid_Robot
        Main/Main_Soft_Rigid_Robot.cpp
        Modules/PIDController.cpp
        Modules/MotorConverter.cpp
        Modules/MPU6050Sensor.cpp
        Modules/MotorDriver.cpp
        Modules/ServoActuation.cpp
        Modules/Navigation.cpp
        )

pico_set_program_name(Soft_Rigid_Robot "Soft_Rigid_Robot")
pico_set_program_version(Soft_Rigid_Robot "0.1")

pico_enable_stdio_uart(Soft_Rigid_Robot 0)
pico_enable_stdio_usb(Soft_Rigid_Robot 1)

target_include_directories(Soft_Rigid_Robot PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}
        ${CMAKE_CURRENT_LIST_DIR}/Modules
)

target_link_libraries(Soft_Rigid_Robot
        pico_stdlib
        hardware_i2c
        hardware_pwm
        )

pico_add_extra_outputs(Soft_Rigid_Robot)


# Troubleshooting executables

add_executable(I2CScanner
        Troubleshooting/IMU/I2CScanner.cpp
        )

pico_enable_stdio_uart(I2CScanner 0)
pico_enable_stdio_usb(I2CScanner 1)

target_link_libraries(I2CScanner
        pico_stdlib
        hardware_i2c
        )

pico_add_extra_outputs(I2CScanner)



add_executable(AngleMeasurement
        Troubleshooting/IMU/AngleMeasurement.cpp
        )

pico_enable_stdio_uart(AngleMeasurement 0)
pico_enable_stdio_usb(AngleMeasurement 1)

target_link_libraries(AngleMeasurement
        pico_stdlib
        hardware_i2c
        )

pico_add_extra_outputs(AngleMeasurement)



add_executable(MotorActuation
        "Troubleshooting/DC Motors/MotorActuation.cpp"
        )

pico_enable_stdio_uart(MotorActuation 0)
pico_enable_stdio_usb(MotorActuation 1)

target_link_libraries(MotorActuation
        pico_stdlib
        hardware_pwm
        )

pico_add_extra_outputs(MotorActuation)



add_executable(ServoActuationTester
        Troubleshooting/Servo/ServoActuationTester.cpp
        )

pico_enable_stdio_uart(ServoActuationTester 0)
pico_enable_stdio_usb(ServoActuationTester 1)

target_link_libraries(ServoActuationTester
        pico_stdlib
        hardware_pwm
        )

pico_add_extra_outputs(ServoActuationTester)



add_executable(EasyServoActuation
        Troubleshooting/Servo/EasyServoActuation.cpp
        )

pico_enable_stdio_uart(EasyServoActuation 0)
pico_enable_stdio_usb(EasyServoActuation 1)

target_link_libraries(EasyServoActuation
        pico_stdlib
        hardware_pwm
        )

pico_add_extra_outputs(EasyServoActuation)



add_executable(MotorMpuDebug
        Troubleshooting/Combinations/MotorMpuDebug.cpp
        )

pico_enable_stdio_uart(MotorMpuDebug 0)
pico_enable_stdio_usb(MotorMpuDebug 1)

target_link_libraries(MotorMpuDebug
        pico_stdlib
        hardware_pwm
        hardware_i2c
        )

pico_add_extra_outputs(MotorMpuDebug)