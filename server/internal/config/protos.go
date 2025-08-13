// Package config provides centralized configuration management using Viper.
package config

// Config holds the complete application configuration
type Config struct {
	Server ServerConfig `mapstructure:"server"`
	Lean   LeanConfig   `mapstructure:"lean"`
	Logger LoggerConfig `mapstructure:"logger"`
}

// ServerConfig contains server-specific configuration
type ServerConfig struct {
	Host string `mapstructure:"host"`
	Port int    `mapstructure:"port"`
}

// LeanConfig contains Lean-specific configuration
type LeanConfig struct {
	Executable  string `mapstructure:"executable"`
	Workspace   string `mapstructure:"workspace"`
	Concurrency int    `mapstructure:"concurrency"`
}

// LoggerConfig contains logging configuration
type LoggerConfig struct {
	Level      string `mapstructure:"level"`
	Production bool   `mapstructure:"production"`
	OutputPath string `mapstructure:"output_path"`
}
