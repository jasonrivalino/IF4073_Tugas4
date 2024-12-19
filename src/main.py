import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

from conventional.classification.knn import knn
from conventional.classification.svm import svm

from deep_learning.preprocessing import *
from deep_learning.model import *

PAD_SMALLER = 10
PAD_DEFAULT = 20
PAD_HIGHER = 40
INPUT_IMAGE = None
INPUT_IMAGE_PATH = None
RESULT_IMAGE = None
IMAGE_WIDTH = 480
IMAGE_HEIGHT = 270
DL_MODEL = None

def configure_grid(layout: tk.Tk, row: int, col: int, row_weight: list = None, col_weight: list = None, row_minsize: list = None, col_minsize: list = None):
  # Assume len(row_weight) = row and len(col_weight) = col
  for i in range(row):
    if (row_minsize is not None and row_minsize[i] is not None):
      layout.rowconfigure(i, weight=row_weight[i], minsize=row_minsize[i])
    else:
      layout.rowconfigure(i, weight=row_weight[i])

  for j in range(col):
    if (col_minsize is not None and col_minsize[j] is not None):
      layout.columnconfigure(j, weight=col_weight[j], minsize=col_minsize[j])
    else:
      layout.columnconfigure(j, weight=col_weight[j])


def select_input_image():
    global INPUT_IMAGE, INPUT_IMAGE_PATH
    # Open a file dialog to select an image
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    filename = file_path.split("/")[-1]

    if file_path:
        # Display the selected file path
        selected_image_name.config(text=f"{filename}", fg="blue")
        INPUT_IMAGE_PATH = file_path
         # Load and display the image
        img = Image.open(file_path)
        INPUT_IMAGE = img
        img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(img)

        image_display_input_img.config(image=img_tk)
        image_display_input_img.image = img_tk  # Keep a reference to avoid garbage collection  
    else:
        selected_image_name.config(text="No Selected Image", fg='red')

def load_model():
    global DL_MODEL
    if DL_MODEL is None:
        data_dir = './training_dataset/dataset (1)'
        filepaths, labels = generate_data_paths(data_dir)
        df = create_df(filepaths, labels)

        train_df, valid_df, test_df = split_dataset(df)
        train_gen, valid_gen, test_gen = generate_image_data(train_df, valid_df, test_df)

        DL_MODEL = create_model_structure(train_gen)
        DL_MODEL.load_weights('./src/deep_learning/my_model_weights.h5')
    
    return DL_MODEL

def process_image():
    global RESULT_IMAGE
    img = INPUT_IMAGE  # Use your input image here
    img_path = INPUT_IMAGE_PATH
    if img is not None:
        selection = method_dropdown_dropdown.get()
        if selection == "Conventional":
            # Load dataset
            dataset_path = ["training_dataset/dataset (1)"]
            # Use this if needed: "training_dataset/dataset (2)"
            prediction, proba = svm(dataset_path, img)
            
            # Add text overlay with the predicted class
            overlay_img = img.copy()
            draw = ImageDraw.Draw(overlay_img)
            font = ImageFont.load_default()
                
            text = f"Class: {prediction[0]}"
            text_position = (20, 20)  # Adjust position as needed
            text_color = (255, 0, 0)  # Red color for the text
            draw.text(text_position, text, fill=text_color, font=font)
            
            accuracy_text = f"Accuracy: {proba.max() * 100:.2f}%"
            accuracy_position = (20, 40)  # Adjust position as needed
            draw.text(accuracy_position, accuracy_text, fill=text_color, font=font)

            RESULT_IMAGE = overlay_img
        else:  # selection == "Deep Learning"
            # TO DO
            print("Deep Learning")
            
            model = load_model()
            class_labels = ['Bus', 'Car', 'Truck', 'Motorcycle']
            predicted_class_label = predict_class(img_path, model, class_labels)
            print(predicted_class_label)

            RESULT_IMAGE = img  # Placeholder for detection function
        result_img = RESULT_IMAGE.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(result_img)
        image_display_result_img.config(image=img_tk)
        image_display_result_img.image = img_tk
    else:
        print("[ERROR] INPUT_IMAGE is None")
    return img

if __name__ == "__main__":
  # Create the main application window
  root = tk.Tk()
  root.title("Vehicle Recognition")
  root.geometry("1280x720")
  # Set the window to fullscreen
  # root.state("zoomed")
  configure_grid(root, 1, 3, [1], [0,4,0], None, [300, None, 300])

  # Style Dropdown
  style = ttk.Style()
  style.configure("TCombobox", font=("Helvetica", 12), background="white", padding=PAD_SMALLER)


  ######################################################
  # Control panel
  panel = tk.Frame(root)
  panel.grid(row=0, column=0, sticky='nesw', padx=PAD_DEFAULT, pady=PAD_DEFAULT)
  configure_grid(panel, 8, 1, [1,1,1,1,1,1,1,1], [1]) 

  # Title
  title = tk.Label(panel, text="Vehicle Recognition", font=("Helvetica", 16, "bold"))
  title.grid(row=0, column=0, sticky='nsew')


  # Image Input Buttons
  image_input_grid = tk.Frame(panel)
  image_input_grid.grid(row=1, column=0, sticky='nsew')
  configure_grid(image_input_grid, 2, 2, [1, 1], [1, 1], None, [200, None])
  # Top Left: Label
  image_input_label = tk.Label(image_input_grid, text="Input Image", font=("Helvetica", 12, "bold"), padx=PAD_DEFAULT)
  image_input_label.grid(row=0, column=0, sticky="wns")
  # Top Right : Button
  button = tk.Button(image_input_grid, text="Browse Image...", command=select_input_image, font=("Helvetica", 12), bg='white', cursor="hand2", padx=PAD_DEFAULT)
  button.grid(row=0, column=1)
  # Bottom Left: Selected Name
  selected_image_name = tk.Label(image_input_grid, text="No Selected Image", font=("Helvetica", 12), fg="red", padx=PAD_DEFAULT)
  selected_image_name.grid(row=1, column=0, sticky="wn")


  # Method Dropdown
  method_dropdown_grid = tk.Frame(panel)
  method_dropdown_grid.grid(row=2, column=0, sticky="nsew")
  configure_grid(method_dropdown_grid, 1, 2, [1], [1, 1], None, [200, None])
  # Label
  method_dropdown_label = tk.Label(method_dropdown_grid, text="Recognition Method", font=("Helvetica", 12, "bold"), padx=PAD_DEFAULT)
  method_dropdown_label.grid(row=0, column=0, sticky="nsw")
  # Dropdown
  method_options = ['Conventional', 'Deep Learning']
  method_dropdown_dropdown = ttk.Combobox(method_dropdown_grid, values=method_options, state="readonly", cursor="hand2")
  method_dropdown_dropdown.set("Conventional")
  method_dropdown_dropdown.grid(row=0, column=1, sticky="ew")


  # Execute Button
  execute_button = tk.Button(panel, text="Execute", command=process_image, font=("Helvetica", 16, "bold"), bg="black", fg="white", cursor="hand2", padx=PAD_HIGHER, pady=PAD_SMALLER)
  execute_button.grid(row=3, column=0, padx=PAD_DEFAULT)


  ######################################################
  # Image display
  img_display_grid = tk.Frame(root, bg='white', padx=PAD_DEFAULT, pady=PAD_DEFAULT)
  img_display_grid.grid(row=0, column=1, sticky='nsew')
  configure_grid(img_display_grid, 2, 1, [1, 1], [1])

  # Display Input
  image_display_input_grid = tk.Frame(img_display_grid, bg="white")
  image_display_input_grid.grid(row=0, column=0, sticky="news")
  configure_grid(image_display_input_grid, 2, 1, [0, 1], [1], [20, IMAGE_HEIGHT])
  image_display_input_label = tk.Label(image_display_input_grid, text="Input Image Display", font=("Helvetica", 16, "bold"), pady=PAD_DEFAULT)
  image_display_input_label.grid(row=0, column=0, sticky="news")
  image_display_input_img = tk.Label(image_display_input_grid, bg="white")
  image_display_input_img.grid(row=1, column=0, sticky="news")


  # Display Result
  image_display_result_grid = tk.Frame(img_display_grid, bg="white")
  image_display_result_grid.grid(row=1, column=0, sticky="news")
  configure_grid(image_display_result_grid, 2, 1, [0, 1], [1], [20, IMAGE_HEIGHT])
  image_display_result_label = tk.Label(image_display_result_grid, text="Result Image Display", font=("Helvetica", 16, "bold"), pady=PAD_DEFAULT)
  image_display_result_label.grid(row=0, column=0, sticky="news")
  image_display_result_img = tk.Label(image_display_result_grid, bg="white")
  image_display_result_img.grid(row=1, column=0, sticky="news")

  ######################################################
  # Result Panel
  result_panel = tk.Frame(root)
  result_panel.grid(row=0, column=2, sticky='nesw', padx=PAD_DEFAULT, pady=PAD_DEFAULT)
  configure_grid(result_panel, 2, 1, [0, 1], [1])

  result_panel_title = tk.Label(result_panel, text="Result Log", font=("Helvetica", 16, "bold"))
  result_panel_title.grid(row=0, column=0, sticky='nsew')

  # Run the application
  root.mainloop()