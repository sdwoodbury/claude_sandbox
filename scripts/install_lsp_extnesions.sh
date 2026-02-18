#!/bin/bash

claude -p "/plugin marketplace add boostvolt/claude-code-lsps" && \
claude -p "/plugin install rust-analyzer-lsp"
# for later: claude -p "/plugin install clangd-lsp"
