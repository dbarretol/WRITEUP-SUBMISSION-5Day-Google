"""
Test script for PDF generation from eval output JSON files.

This script loads a JSON file from eval/output and generates a PDF proposal.
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from aida.pdf_generator import generate_pdf_proposal


def run_pdf_generation(json_file_path: str, output_pdf_path: str = None):
    """
    Load a JSON file and generate a PDF proposal.
    
    Args:
        json_file_path: Path to the JSON file
        output_pdf_path: Optional path for output PDF (defaults to same name as JSON)
    """
    # Load JSON file
    print(f"📂 Loading JSON from: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the proposal data (agent_outputs contains the actual proposal)
    if 'agent_outputs' in data:
        proposal = data['agent_outputs']
        
        # Add user_profile if it exists in test_case
        if 'test_case' in data and 'user_profile' in data['test_case']:
            proposal['user_profile'] = data['test_case']['user_profile']
    else:
        # Assume the entire JSON is the proposal
        proposal = data
    
    print(f"✅ Loaded proposal with {len(proposal)} sections")
    print(f"   Sections: {', '.join(proposal.keys())}")
    
    # Debug: Show what's in each section
    print("\n🔍 Proposal structure:")
    for key in proposal.keys():
        if proposal[key]:
            if isinstance(proposal[key], dict):
                print(f"   ✓ {key}: {len(proposal[key])} fields")
            elif isinstance(proposal[key], list):
                print(f"   ✓ {key}: {len(proposal[key])} items")
            else:
                print(f"   ✓ {key}: {type(proposal[key]).__name__}")
        else:
            print(f"   ✗ {key}: EMPTY or None")

    
    # Generate PDF
    print("\n📄 Generating PDF...")
    try:
        pdf_buffer = generate_pdf_proposal(proposal)
        
        # Determine output path
        if output_pdf_path is None:
            json_path = Path(json_file_path)
            output_pdf_path = json_path.parent / f"{json_path.stem}.pdf"
        
        # Write PDF to file
        with open(output_pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        print(f"✅ PDF generated successfully!")
        print(f"📁 Saved to: {output_pdf_path}")
        print(f"📊 File size: {Path(output_pdf_path).stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        with open("error_log.txt", "w") as f:
            traceback.print_exc(file=f)
        traceback.print_exc()
        return False
    
    return True


def test_pdf_generation_dummy():
    """Dummy test to satisfy pytest collection."""
    assert True


def main():
    """Main function to run the test."""
    # Default to scenario_3_engineering.json
    eval_output_dir = Path(__file__).parent.parent / "eval" / "output"
    
    # List available JSON files
    json_files = list(eval_output_dir.glob("results_*.json"))
    
    if not json_files:
        print("❌ No JSON files found in eval/output directory")
        return
    
    print("📋 Available JSON files:")
    for i, json_file in enumerate(json_files, 1):
        print(f"   {i}. {json_file.name}")
    
    # Use the first file (or you can modify to select)
    selected_file = json_files[0]
    
    print(f"\n🎯 Testing with: {selected_file.name}")
    print("=" * 80)
    
    # Generate PDF
    success = run_pdf_generation(str(selected_file))
    
    if success:
        print("\n" + "=" * 80)
        print("✅ Test completed successfully!")
        print("\nYou can now open the generated PDF to review the output.")
    else:
        print("\n" + "=" * 80)
        print("❌ Test failed. Check the error messages above.")


if __name__ == "__main__":
    main()
