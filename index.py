import streamlit as st
from pytubefix import YouTube
from io import BytesIO

st.title("🎥 YouTube Downloader (with itag search & sort)")

url = st.text_input("Enter YouTube video URL:")

if url:
    try:
        yt = YouTube(url)
        st.subheader(f"📺 {yt.title}")
        st.write(f"⏱️ Length: {yt.length} sec")
        st.write(f"👁️ Views: {yt.views:,}")

        streams = yt.streams
        stream_data = {str(s.itag): s for s in streams}

        # Search and Sort Controls
        sort_option = st.selectbox("Sort streams by:", ["itag", "type", "resolution"])
        search_query = st.text_input("🔍 Filter by keyword (e.g., 720p, audio, mp4)")

        # Filter and sort streams
        def stream_key(s):
            if sort_option == "type":
                return s.type
            elif sort_option == "resolution":
                return s.resolution or ""
            return s.itag

        filtered_streams = [
            s for s in streams
            if search_query.lower() in str(s.itag).lower()
            or search_query.lower() in (s.type or '').lower()
            or search_query.lower() in (s.resolution or '').lower()
            or search_query.lower() in (s.mime_type or '').lower()
        ] if search_query else streams

        filtered_streams = sorted(filtered_streams, key=stream_key)

        if filtered_streams:
            st.write("🎞️ Available Streams:")
            for s in filtered_streams:
                # Estimate file size
                file_size = "N/A"
                if hasattr(s, 'bitrate') and s.bitrate and yt.length:
                    try:
                        # Convert bitrate from bps to MB
                        size_in_mb = (int(s.bitrate) * yt.length) / (8 * 1024 * 1024)
                        file_size = f"{size_in_mb:.2f}MB"
                    except:
                        pass
                
                st.write(
                    f"itag: {s.itag} | Type: {s.type} | "
                    f"Res: {s.resolution or 'N/A'} | FPS: {getattr(s, 'fps', 'N/A')} | "
                    f"Bitrate: {getattr(s, 'abr', 'N/A')} | Size: {file_size} | Mime: {s.mime_type}"
                )

            selected_itag = st.text_input("Enter itag to download:")

            if selected_itag in stream_data:
                selected_stream = stream_data[selected_itag]
                
                # Show estimated file size before download
                if hasattr(selected_stream, 'bitrate') and selected_stream.bitrate and yt.length:
                    try:
                        size_in_mb = (int(selected_stream.bitrate) * yt.length) / (8 * 1024 * 1024)
                        st.info(f"Estimated file size: {size_in_mb:.2f} MB")
                    except:
                        st.info("Could not estimate file size")
                
                if st.button("Download"):
                    buffer = BytesIO()
                    selected_stream.stream_to_buffer(buffer)
                    buffer.seek(0)

                    ext = selected_stream.mime_type.split('/')[-1]
                    filename = f"{yt.title}.{ext}".replace(" ", "_")

                    st.success("✅ Download Ready")
                    st.download_button(
                        label="💾 Save File",
                        data=buffer,
                        file_name=filename,
                        mime=selected_stream.mime_type
                    )
            elif selected_itag:
                st.error("❌ Invalid itag selected.")
        else:
            st.warning("No streams matched your filter.")

    except Exception as e:
        st.error(f"Error: {e}")
