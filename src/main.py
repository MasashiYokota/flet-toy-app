import csv
import os
import re
import time

import flet as ft
import spacy

nlp = spacy.load("ja_ginza")  # GiNZAモデルの読み込み
katakana_regex = r"[ァ-ンー]+"
email_regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
phone_regex = (
    r"[\(]{0,1}[0-9０-９]{2,4}[\)\(-|ー)\(]{0,1}[0-9０-９]{2,4}[\)(-|ー)]{0,1}[0-9０-９]{3,4}"
)


def mask_text(text: str):
    doc = nlp(text)
    masked_text = ""
    for sent in doc.sents:
        masked_text += "".join(
            [
                "[name]"
                if token.tag_.startswith("名詞-固有名詞-人名")
                and not re.search(
                    katakana_regex, token.text
                )  # パーカーは人命にもなりうるが服のパーカーとも被るのでカタカナ名は無視する
                else token.text
                for token in sent
            ]
        )

    masked_text = re.sub(email_regex, "[masked email]", masked_text)

    masked_text = re.sub(phone_regex, "[masked phone number]", masked_text)

    return masked_text


def main(page: ft.Page):
    page.title = "pochi-mas"

    # Status text to show upload/download status
    status_text = ft.Text("CSVファイルをアップロードしてください", size=16)

    # Progress bar for processing
    progress_bar = ft.ProgressBar(width=400, visible=False)
    progress_text = ft.Text("", size=14, visible=False)

    # Column selection container
    column_selection_container = ft.Container(visible=False)
    selected_columns = []
    uploaded_file_path = ""

    # Process the file with selected columns
    def process_file_with_columns():
        nonlocal uploaded_file_path

        try:
            # First, count total lines for progress tracking
            status_text.value = "ファイルの行数を確認中..."
            status_text.update()

            with open(uploaded_file_path, encoding="utf-8") as input_file:
                csv_reader = csv.reader(input_file)
                headers = next(csv_reader)
                total_lines = sum(1 for _ in csv_reader)

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
            file_name = os.path.basename(uploaded_file_path)
            output_filename = f"masked_{file_name}"
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

            with (
                open(uploaded_file_path, encoding="utf-8") as input_file,
                open(output_path, "w", encoding="utf-8") as output_file,
            ):
                # Use DictReader to read CSV with column names
                csv_reader = csv.DictReader(input_file)
                csv_writer = csv.writer(output_file)

                # Write header to output file
                csv_writer.writerow(headers)

                for line_number, row in enumerate(
                    csv_reader, 2
                ):  # Start from 2 because header is line 1
                    # Update progress bar
                    progress_value = line_number / total_lines
                    progress_bar.value = progress_value
                    progress_percentage = int(progress_value * 100)
                    progress_text.value = f"{progress_percentage}%"

                    # Calculate estimated time remaining
                    if line_number > 2:
                        elapsed_time = time.time() - start_time
                        avg_time_per_line = elapsed_time / (line_number - 2)
                        remaining_lines = total_lines - line_number + 1
                        estimated_remaining_time = avg_time_per_line * remaining_lines

                        # Format time display
                        if estimated_remaining_time > 60:
                            time_display = f"{int(estimated_remaining_time // 60)}分{int(estimated_remaining_time % 60)}秒"
                        else:
                            time_display = f"{int(estimated_remaining_time)}秒"

                        status_text.value = (
                            f"処理中... {line_number}/{total_lines} 行目 (残り約{time_display})"
                        )
                    else:
                        status_text.value = f"処理中... {line_number}/{total_lines} 行目"

                    # Update UI every 10 lines or on the last line for better performance
                    if line_number % 10 == 0 or line_number == total_lines:
                        status_text.update()
                        progress_bar.update()
                        progress_text.update()

                    # Apply masking only to selected columns
                    values = [
                        mask_text(row[column]) if column in selected_columns else row[column]
                        for column in headers
                    ]

                    # Write processed line to output file
                    csv_writer.writerow(values)

            # Hide progress bar and show completion message
            progress_bar.visible = False
            progress_text.visible = False
            column_selection_container.visible = False
            progress_bar.update()
            progress_text.update()
            column_selection_container.update()

            status_text.value = f"完了! ファイル '{file_name}' を処理して {output_filename} としてダウンロードフォルダに保存しました"
        except Exception as ex:
            # Hide progress bar on error
            progress_bar.visible = False
            progress_text.visible = False
            column_selection_container.visible = False
            progress_bar.update()
            progress_text.update()
            column_selection_container.update()

            status_text.value = f"エラー: {str(ex)}"

        status_text.update()

    # File picker for uploading CSV files
    def pick_files_result(e: ft.FilePickerResultEvent):
        if not e.files:
            status_text.value = "エラー: ファイルが設定されていません。"
            status_text.update()
            return

        nonlocal uploaded_file_path, selected_columns
        selected_columns = []

        # Get the first selected file
        uploaded_file = e.files[0]
        uploaded_file_path = uploaded_file.path

        try:
            # Read the CSV header to get column names
            with open(uploaded_file_path, encoding="utf-8") as input_file:
                header = input_file.readline().strip()
                columns = header.split(",")

            # Create checkboxes for column selection
            column_checkboxes = []

            def checkbox_changed(e):
                nonlocal selected_columns
                if e.control.value:
                    if e.control.data not in selected_columns:
                        selected_columns.append(e.control.data)
                else:
                    if e.control.data in selected_columns:
                        selected_columns.remove(e.control.data)

            for column in columns:
                checkbox = ft.Checkbox(
                    label=column, value=False, data=column, on_change=checkbox_changed
                )
                column_checkboxes.append(checkbox)

            # Create a button to start processing
            process_button = ft.ElevatedButton(
                "選択したカラムをマスキングする", on_click=lambda _: process_file_with_columns()
            )

            # Update the column selection container
            column_selection_container.content = ft.Column(
                [
                    ft.Text(
                        "マスキングするカラムを選択してください:",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Divider(),
                    ft.Column(column_checkboxes, scroll=ft.ScrollMode.AUTO, height=200),
                    process_button,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

            column_selection_container.visible = True
            column_selection_container.update()

            status_text.value = f"ファイル '{uploaded_file.name}' をアップロードしました。マスキングするカラムを選択してください。"
            status_text.update()

        except Exception as ex:
            status_text.value = f"エラー: {str(ex)}"
            status_text.update()

    file_picker = ft.FilePicker(on_result=pick_files_result)
    page.overlay.append(file_picker)

    # Upload button
    upload_button = ft.ElevatedButton(
        "CSVファイルをアップロード",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["csv"]),
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
                            "CSVをアップロードして特定のカラムの人名をマスキングします",
                        ),
                        ft.Divider(),
                        status_text,
                        progress_text,
                        progress_bar,
                        column_selection_container,
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


if __name__ == "__main__":
    ft.app(main)
