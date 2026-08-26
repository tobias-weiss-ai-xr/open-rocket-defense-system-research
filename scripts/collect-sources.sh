#!/bin/bash
# Source Collection Script
# Collects and organizes research sources

set -e

echo "=== Ukrainian Missile Defense Research ==="
echo "Collecting sources for cost-effective alternatives analysis"
echo ""

# Create source directories
mkdir -p sources/primary
mkdir -p sources/secondary
mkdir -p sources/osint
mkdir -p sources/data

# Function to add source
add_source() {
    local category=$1
    local title=$2
    local url=$3
    local date=$4
    
    echo "[$category] $title" >> sources/README.md
    echo "  URL: $url" >> sources/README.md
    echo "  Retrieved: $date" >> sources/README.md
    echo "" >> sources/README.md
}

echo "Source collection framework ready"
echo "Add sources manually or use browser automation to scrape"
echo ""
echo "Categories:"
echo "  - sources/primary/    (gov reports, manufacturer docs)"
echo "  - sources/secondary/  (think tanks, academic papers)"
echo "  - sources/osint/      (visual intel, social media)"
echo "  - sources/data/       (datasets, spreadsheets)"
