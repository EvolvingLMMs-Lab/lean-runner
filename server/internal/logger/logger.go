// Package logger provides a centralized logger configuration using zap.
package logger

import (
	"fmt"
	"os"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var (
	// Global logger instance
	Logger *zap.Logger
	// Sugar provides a more convenient, loosely typed API
	Sugar *zap.SugaredLogger
)

// LogLevel represents the logging level
type LogLevel string

const (
	DebugLevel LogLevel = "debug"
	InfoLevel  LogLevel = "info"
	WarnLevel  LogLevel = "warn"
	ErrorLevel LogLevel = "error"
)

// Config holds the logger configuration
type Config struct {
	Level      LogLevel `json:"level"`
	Production bool     `json:"production"`
	OutputPath string   `json:"output_path"`
}

// DefaultConfig returns a default logger configuration
func DefaultConfig() *Config {
	return &Config{
		Level:      InfoLevel,
		Production: false,
		OutputPath: "stdout",
	}
}

// Initialize sets up the global logger with the given configuration
func Initialize(config *Config) error {
	var zapConfig zap.Config

	if config.Production {
		// Production configuration - JSON formatted, structured logs
		zapConfig = zap.NewProductionConfig()
		zapConfig.EncoderConfig.TimeKey = "timestamp"
		zapConfig.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	} else {
		// Development configuration - colored, human-readable logs
		zapConfig = zap.NewDevelopmentConfig()
		zapConfig.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
		zapConfig.EncoderConfig.EncodeTime = zapcore.TimeEncoderOfLayout("15:04:05")
		zapConfig.EncoderConfig.EncodeCaller = zapcore.ShortCallerEncoder
	}

	// Set log level
	switch config.Level {
	case DebugLevel:
		zapConfig.Level = zap.NewAtomicLevelAt(zap.DebugLevel)
	case InfoLevel:
		zapConfig.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
	case WarnLevel:
		zapConfig.Level = zap.NewAtomicLevelAt(zap.WarnLevel)
	case ErrorLevel:
		zapConfig.Level = zap.NewAtomicLevelAt(zap.ErrorLevel)
	default:
		// Log a warning for invalid log level and use InfoLevel as fallback
		fmt.Printf("Warning: Invalid log level '%s'. Using 'info' level instead.\n", config.Level)
		fmt.Printf("Valid log levels are: debug, info, warn, error\n")
		zapConfig.Level = zap.NewAtomicLevelAt(zap.InfoLevel)
	}

	// Set output paths
	if config.OutputPath != "" && config.OutputPath != "stdout" {
		zapConfig.OutputPaths = []string{config.OutputPath}
		zapConfig.ErrorOutputPaths = []string{config.OutputPath}
	}

	// Build the logger
	logger, err := zapConfig.Build(
		zap.AddCaller(),
		zap.AddCallerSkip(1), // Skip one level to show the actual caller, not this wrapper
	)
	if err != nil {
		return err
	}

	// Set global logger instances
	Logger = logger
	Sugar = logger.Sugar()

	return nil
}

// InitializeFromEnv initializes the logger from environment variables
func InitializeFromEnv() error {
	config := DefaultConfig()

	// Read from environment variables
	if level := os.Getenv("LOG_LEVEL"); level != "" {
		config.Level = LogLevel(level)
	}

	if os.Getenv("PRODUCTION") == "true" || os.Getenv("ENV") == "production" {
		config.Production = true
	}

	if outputPath := os.Getenv("LOG_OUTPUT"); outputPath != "" {
		config.OutputPath = outputPath
	}

	return Initialize(config)
}

// Sync flushes any buffered log entries
func Sync() {
	if Logger != nil {
		Logger.Sync()
	}
}

// GetLogger returns the global logger instance
func GetLogger() *zap.Logger {
	if Logger == nil {
		// Fallback to a default logger if not initialized
		InitializeFromEnv()
	}
	return Logger
}

// GetSugar returns the global sugar logger instance
func GetSugar() *zap.SugaredLogger {
	if Sugar == nil {
		// Fallback to a default logger if not initialized
		InitializeFromEnv()
	}
	return Sugar
}

// Convenience functions for common logging operations

// Info logs an info message
func Info(msg string, fields ...zap.Field) {
	GetLogger().Info(msg, fields...)
}

// Debug logs a debug message
func Debug(msg string, fields ...zap.Field) {
	GetLogger().Debug(msg, fields...)
}

// Warn logs a warning message
func Warn(msg string, fields ...zap.Field) {
	GetLogger().Warn(msg, fields...)
}

// Error logs an error message
func Error(msg string, fields ...zap.Field) {
	GetLogger().Error(msg, fields...)
}

// Fatal logs a fatal message and exits the program
func Fatal(msg string, fields ...zap.Field) {
	GetLogger().Fatal(msg, fields...)
}

// Convenience functions using sugared logger (printf-style)

// Infof logs an info message with printf-style formatting
func Infof(template string, args ...interface{}) {
	GetSugar().Infof(template, args...)
}

// Debugf logs a debug message with printf-style formatting
func Debugf(template string, args ...interface{}) {
	GetSugar().Debugf(template, args...)
}

// Warnf logs a warning message with printf-style formatting
func Warnf(template string, args ...interface{}) {
	GetSugar().Warnf(template, args...)
}

// Errorf logs an error message with printf-style formatting
func Errorf(template string, args ...interface{}) {
	GetSugar().Errorf(template, args...)
}

// Fatalf logs a fatal message with printf-style formatting and exits the program
func Fatalf(template string, args ...interface{}) {
	GetSugar().Fatalf(template, args...)
}
