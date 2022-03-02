#!/bin/bash

cowsay "Building Linux (amd64)..."
env GOOS=linux GOARCH=amd64 go build -o bin/no-role-kick-linux-amd64

cowsay "Building Windows (amd64)..."
env GOOS=windows GOARCH=amd64 go build -o bin/no-role-kick-windows-amd64.exe

cowsay "Building MacOS (amd64)..."
env GOOS=darwin GOARCH=amd64 go build -o bin/no-role-kick-darwin-amd64

cowsay "Build complete!"