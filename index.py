import streamlit as st
from pytubefix import YouTube
from io import BytesIO

st.title("🎥 YouTube Video Downloader")

# Step 1: Input YouTube URL
url = st.text_input("Enter YouTube video URL:")

if url:
    try:
        yt = YouTube(url)
        st.subheader(f"Title: {yt.title}")
        st.write(f"Length: {yt.length} seconds")
        st.write(f"Views: {yt.views}")

        # Step 2: Show available streams
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        stream_data = {str(s.itag): s for s in streams}
        
        if stream_data:
            st.write("Available streams:")
            for itag, stream in stream_data.items():
                st.write(f"itag: {itag} | Resolution: {stream.resolution} | FPS: {stream.fps} | Type: {stream.mime_type}")
            
            # Step 3: Ask user to select an itag
            selected_itag = st.text_input("Enter itag of the stream you want to download:")
            
            if selected_itag in stream_data:
                if st.button("Download"):
                    selected_stream = stream_data[selected_itag]
                    buffer = BytesIO()
                    selected_stream.stream_to_buffer(buffer)
                    buffer.seek(0)

                    st.success("Download ready!")
                    
                    # Step 4: Provide download button
                    st.download_button(
                        label="💾 Save video file",
                        data=buffer,
                        file_name=f"{yt.title}.mp4",
                        mime='video/mp4'
                    )
            elif selected_itag:
                st.error("Invalid itag selected. Please try again.")

        else:
            st.warning("No progressive MP4 streams found.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
