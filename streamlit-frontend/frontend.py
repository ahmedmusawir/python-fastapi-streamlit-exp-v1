import streamlit as st


def main():
  st.title('My Recipe 👨‍🍳')
  st.header('Upload an Image to make a Recipe')

  uploaded_file = st.file_uploader('Pick and Image', type=['jpg', 'png'])

  if uploaded_file is not None:
    print(uploaded_file)
    # Collecting the img file 
    file_bytes = uploaded_file.getvalue()

    # Preparing the img folder
    folder_path = './_imgs'

    # Ensuring tht folder exists, if not it will be created
    import os
    if not os.path.exists(folder_path):
      os.makedirs(folder_path)

    # Creating the file name with path
    file_w_path = os.path.join(folder_path, uploaded_file.name)

    # Creating the uploaded file locally
    with open(file_w_path, 'wb') as file:
      file.write(file_bytes)
    
    st.image(uploaded_file,
             caption='Uploaded File',
             use_column_width=True)


if __name__ == '__main__':
  main()
