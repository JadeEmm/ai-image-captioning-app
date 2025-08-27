"""
🖼️ Professional AI Image Captioning App
==========================================

A complete, standalone image captioning application using Salesforce's BLIP model.
Perfect for deployment on GitHub, Hugging Face Spaces, or local development.

Author: [Your Name]
GitHub: https://github.com/[your-username]/ai-image-captioning-app
License: MIT

Usage:
    python app.py

Requirements:
    - Python 3.7+
    - See requirements.txt for dependencies
"""

import gradio as gr
import torch
from transformers import pipeline
from PIL import Image
import sys
import logging
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

class ImageCaptioningApp:
    """
    Professional Image Captioning Application
    
    This class encapsulates the entire image captioning functionality,
    making it easy to maintain, test, and deploy.
    """
    
    def __init__(self):
        """Initialize the app"""
        self.caption_pipeline = None
        self.device = self._get_device()
        self.model_name = "Salesforce/blip-image-captioning-base"
        
        logger.info(f"🖥️ Using device: {self.device}")
        logger.info(f"🤖 Model: {self.model_name}")
    
    def _get_device(self):
        """Determine the best device to use (GPU vs CPU)"""
        if torch.cuda.is_available():
            logger.info("✅ GPU available - will use GPU for faster processing")
            return 0  # GPU
        else:
            logger.info("💻 GPU not available - using CPU")
            return -1  # CPU
    
    def load_model(self):
        """
        Load the AI model using Hugging Face pipeline
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if self.caption_pipeline is not None:
            return True
        
        try:
            logger.info("🔄 Loading BLIP model...")
            logger.info("📥 This may take a few moments on first run...")
            
            # Load the model using the official Hugging Face pipeline
            self.caption_pipeline = pipeline(
                task="image-to-text",
                model=self.model_name,
                device=self.device
            )
            
            logger.info("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            
            # Fallback to CPU if GPU fails
            if self.device == 0:  # If we were trying GPU
                logger.info("🔄 Retrying with CPU...")
                try:
                    self.caption_pipeline = pipeline(
                        task="image-to-text",
                        model=self.model_name,
                        device=-1  # Force CPU
                    )
                    self.device = -1
                    logger.info("✅ Model loaded on CPU!")
                    return True
                except Exception as e2:
                    logger.error(f"❌ CPU fallback also failed: {e2}")
            
            return False
    
    def generate_caption(self, image):
        """
        Generate caption for an uploaded image
        
        Args:
            image (PIL.Image): Input image from Gradio
            
        Returns:
            str: Generated caption or error message
        """
        # Validate input
        if image is None:
            return "❌ Please upload an image first!"
        
        # Load model if not already loaded
        if not self.load_model():
            return ("❌ Failed to load AI model. This might be due to:\n"
                   "• Internet connection issues\n"
                   "• Insufficient memory\n"
                   "• Missing dependencies\n\n"
                   "Please try restarting the application.")
        
        try:
            logger.info("🔍 Processing image...")
            
            # Ensure image is in RGB format
            if image.mode != 'RGB':
                image = image.convert('RGB')
                logger.info("🔄 Converted image to RGB format")
            
            # Generate caption using the pipeline
            result = self.caption_pipeline(image)
            
            # Extract caption from result
            if result and len(result) > 0:
                caption = result[0]['generated_text']
                logger.info(f"✅ Generated caption: '{caption}'")
                
                # Clean up the caption (remove extra spaces, etc.)
                caption = caption.strip()
                
                return f"🎯 {caption}"
            else:
                logger.warning("⚠️ Model returned empty result")
                return "❌ Could not generate a caption for this image."
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error during caption generation: {error_msg}")
            
            # Provide helpful error messages
            if "out of memory" in error_msg.lower():
                return ("❌ Out of memory error. Try:\n"
                       "• Using a smaller image\n"
                       "• Restarting the application\n"
                       "• Using CPU instead of GPU")
            elif "connection" in error_msg.lower():
                return "❌ Network error. Please check your internet connection."
            else:
                return f"❌ Processing error: {error_msg}"
    
    def create_interface(self):
        """
        Create and configure the Gradio interface
        
        Returns:
            gr.Interface: Configured Gradio interface
        """
        interface = gr.Interface(
            fn=self.generate_caption,
            inputs=[
                gr.Image(
                    label="📷 Upload Any Image",
                    type="pil",
                    sources=["upload", "webcam"],
                    height=400
                )
            ],
            outputs=[
                gr.Textbox(
                    label="🏷️ AI Generated Caption",
                    placeholder="Upload an image and the AI will describe it here...",
                    lines=3,
                    max_lines=6
                )
            ],
            
            title="🖼️ AI Image Captioning App",
            
            description="""
            ## 🚀 Transform any image into words with AI!
            
            Upload any photo and watch as advanced AI describes what it sees. Perfect for:
            
            **✨ Content Creation**
            - Generate alt text for accessibility
            - Create social media captions
            - Automate image descriptions
            
            **🎓 Learning & Fun**
            - Explore how AI "sees" images
            - Test different types of photos
            - Compare AI vs human descriptions
            
            **🔬 How it works:** Uses Salesforce's BLIP model, trained on millions of images to understand and describe visual content.
            """,
            
            article="""
            ### 🛠️ Technical Details
            
            **Model:** Salesforce BLIP (Bootstrapping Language-Image Pre-training)
            - State-of-the-art vision-language model
            - Trained on diverse image-text pairs
            - Excellent at detailed, accurate descriptions
            
            **Infrastructure:**
            - Built with Hugging Face Transformers
            - Optimized for both CPU and GPU
            - Gradio interface for easy interaction
            
            ### 🎯 Tips for Best Results
            
            - **High quality images** work best
            - **Clear, well-lit photos** generate better captions
            - **Single subject focus** produces more accurate descriptions
            - **Common objects/scenes** are described most accurately
            
            ### 🤝 Open Source
            
            This app is completely open source! Check out the code, contribute, or build your own version.
            
            **GitHub:** [Link to your repository]
            **Model:** [Salesforce BLIP on Hugging Face](https://huggingface.co/Salesforce/blip-image-captioning-base)
            
            ---
            
            Made with ❤️ using Python, Transformers, and Gradio
            """,
            
            theme=gr.themes.Soft(),
            allow_flagging="never",
            
            examples=[
                # You can add example images here if you include them in your repo
                # ["examples/dog.jpg"],
                # ["examples/landscape.jpg"],
                # ["examples/people.jpg"]
            ]
        )
        
        return interface
    
    def launch(self, share=False, server_name="127.0.0.1", server_port=7860):
        """
        Launch the Gradio app
        
        Args:
            share (bool): Whether to create a public link
            server_name (str): Server address
            server_port (int): Server port
        """
        interface = self.create_interface()
        
        logger.info("🚀 Launching Image Captioning App...")
        logger.info(f"📡 Server: {server_name}:{server_port}")
        
        if share:
            logger.info("🌐 Creating public share link...")
        
        try:
            interface.launch(
                share=share,
                server_name=server_name,
                server_port=server_port,
                show_error=True,
                quiet=False
            )
        except Exception as e:
            logger.error(f"❌ Failed to launch app: {e}")
            raise

def main():
    """Main function to run the application"""
    
    # Print welcome message
    print("🖼️ AI Image Captioning App")
    print("=" * 50)
    print("🚀 Starting up...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required")
        sys.exit(1)
    
    # Create and launch app
    app = ImageCaptioningApp()
    
    try:
        # Launch with public sharing for demos
        # Set share=False for local development
        app.launch(
            share=True,  # Creates public link - great for demos!
            server_name="0.0.0.0",  # Allow external connections
            server_port=7860
        )
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()