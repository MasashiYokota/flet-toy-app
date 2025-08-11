import flet as ft
import spacy
import os
import time


nlp = spacy.load("ja_ginza")  # GiNZAモデルの読み込み


def mask_text(text: str):
    doc = nlp(text)
    masked_text = ""
    for sent in doc.sents:
        masked_text += "".join(
            [
                "○○" if token.tag_.startswith("名詞-固有名詞-人名") else token.text
                for token in sent
            ]
        )

    return masked_text


def main(page: ft.Page):
    page.title = "pochi mat"

    # Status text to show upload/download status
    status_text = ft.Text("CSVファイルをアップロードしてください", size=16)

    # Progress bar for processing
    progress_bar = ft.ProgressBar(width=400, visible=False)
    progress_text = ft.Text("", size=14, visible=False)

    # File picker for uploading CSV files
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            # Get the first selected file
            uploaded_file = e.files[0]

            # Process the uploaded CSV file line by line and apply mask_text
            try:
                # First, count total lines for progress tracking
                status_text.value = "ファイルの行数を確認中..."
                status_text.update()

                with open(uploaded_file.path, "r", encoding="utf-8") as input_file:
                    total_lines = sum(1 for _ in input_file)

                # Show progress bar and initialize
                progress_bar.visible = True
                progress_text.visible = True
                progress_bar.value = 0
                progress_text.value = "0%"
                status_text.value = f"処理開始: 全{total_lines}行"
                status_text.update()
                progress_bar.update()
                progress_text.update()

                start_time = time.time()

                # Create output filename with masked_ prefix
                output_filename = f"masked_{uploaded_file.name}"
                downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

                # Check if file already exists and create unique filename
                base_output_path = os.path.join(downloads_folder, output_filename)
                output_path = base_output_path
                counter = 1
                is_updated = False
                unique_filename = ""

                while os.path.exists(output_path):
                    is_updated = True
                    name, ext = os.path.splitext(output_filename)
                    unique_filename = f"{name}({counter}){ext}"
                    output_path = os.path.join(downloads_folder, unique_filename)
                    counter += 1

                if is_updated:
                    output_filename = unique_filename

                with open(uploaded_file.path, "r", encoding="utf-8") as input_file:
                    with open(output_path, "w", encoding="utf-8") as output_file:
                        for line_number, line in enumerate(input_file, 1):
                            # Update progress bar
                            progress_value = line_number / total_lines
                            progress_bar.value = progress_value
                            progress_percentage = int(progress_value * 100)
                            progress_text.value = f"{progress_percentage}%"

                            # Calculate estimated time remaining
                            if line_number > 1:
                                elapsed_time = time.time() - start_time
                                avg_time_per_line = elapsed_time / (line_number - 1)
                                remaining_lines = total_lines - line_number + 1
                                estimated_remaining_time = (
                                    avg_time_per_line * remaining_lines
                                )

                                # Format time display
                                if estimated_remaining_time > 60:
                                    time_display = f"{int(estimated_remaining_time // 60)}分{int(estimated_remaining_time % 60)}秒"
                                else:
                                    time_display = f"{int(estimated_remaining_time)}秒"

                                status_text.value = f"処理中... {line_number}/{total_lines} 行目 (残り約{time_display})"
                            else:
                                status_text.value = (
                                    f"処理中... {line_number}/{total_lines} 行目"
                                )

                            # Update UI every 10 lines or on the last line for better performance
                            if line_number % 10 == 0 or line_number == total_lines:
                                status_text.update()
                                progress_bar.update()
                                progress_text.update()

                            masked_line = mask_text(line.strip())
                            output_file.write(masked_line + "\n")

                # Hide progress bar and show completion message
                progress_bar.visible = False
                progress_text.visible = False
                progress_bar.update()
                progress_text.update()

                status_text.value = f"完了! ファイル '{uploaded_file.name}' を処理して {output_filename} としてダウンロードフォルダに保存しました"
            except Exception as ex:
                # Hide progress bar on error
                progress_bar.visible = False
                progress_text.visible = False
                progress_bar.update()
                progress_text.update()

                status_text.value = f"エラー: {str(ex)}"

            status_text.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    # Upload button
    upload_button = ft.ElevatedButton(
        "CSVファイルをアップロード",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False, allowed_extensions=["csv"]
        ),
    )

    page.add(
        ft.SafeArea(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(
                            "ぽちぽち マスキングツール",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "CSVをアップロードすると人名をマスキングします",
                        ),
                        ft.Divider(),
                        status_text,
                        progress_text,
                        progress_bar,
                        upload_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.alignment.center,
                padding=20,
            ),
            expand=True,
        )
    )


ft.app(main)
