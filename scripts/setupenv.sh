#!/bin/bash
    
#create venv
echo -e "Creating Virtual environment names as '.venv'..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo -e "Activating virtual environment..."
case "$OSTYPE" in
    linux-gnu*)
        OS="Linux"
        source .venv/bin/activate
        ;;
    darwin*)
        OS="macOS"
        source .venv/bin/activate
        ;;
    msys*|cygwin*)
        OS="Windows"
        source .venv/Scripts/activate
        ;;
    *)
        OS="Unknown ($OSTYPE)"
        ;;
esac

if [ -z "$VIRTUAL_ENV" ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

echo -e "Installing requirements.."
pip install -r requirements.txt

echo -e "All done!"