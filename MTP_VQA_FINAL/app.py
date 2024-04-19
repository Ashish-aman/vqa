import streamlit as st
from PIL import Image
from demo import demo


def main():
    st.title("Visual Question Answering System")

    # Sidebar
    st.sidebar.title("Options")
    uploaded_img = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    question = st.sidebar.text_input("Enter your question:")

    if st.sidebar.button("Ask"):
        if uploaded_img is not None and question:
            # Display uploaded image
            st.image(uploaded_img, caption="Uploaded Image", use_column_width=True)

            # Process image and question
            answers = demo(uploaded_img, question)

            # Display answers
            st.header("Top 5 Answers:")
            for i, answer in enumerate(answers, 1):
                st.write(f"{i}. {answer}")
        else:
            st.warning("Please upload an image and enter a question.")

    # About section
    st.markdown("### About")
    st.write("This is a Visual Question Answering System powered by machine learning.")

if __name__ == "__main__":
    main()
