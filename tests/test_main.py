from main import mask_text


def test_mask_text__mask_person_name():
    text = "名前は山田太郎です。"
    expected = "名前は[name][name]です。"
    assert mask_text(text) == expected

    text = "名前は山田 太郎です。"
    expected = "名前は[name][name]です。"
    assert mask_text(text) == expected


def test_mask_text__ignore_katakana_person_name():
    # パーカーは人命にもなりうるが
    # 服のパーカーとも被るのでカタカナ名は無視する
    text = "名前はパーカーです。"
    expected = "名前はパーカーです。"
    assert mask_text(text) == expected


def test_mask_text__mask_email_address():
    text = "メアドはtest@gmail.comです。"
    expected = "メアドは[masked email]です。"
    assert mask_text(text) == expected

    text = "メアドは test.test2+test3@company.co.jp です。"
    expected = "メアドは[masked email]です。"
    assert mask_text(text) == expected

    text = "メアドは test.test2+test3@company.xx.co.jp です。"
    expected = "メアドは[masked email]です。"
    assert mask_text(text) == expected


def test_mask_text__mask_phone_number():
    text = "電話番号は 090-1234-5678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は 0120-124-5678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は (0120)124 5678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は 0120(124)5678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は 0120 124 5678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は 01201245678 です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected

    text = "電話番号は ０１２０ー１２３ー４５６７ です。"
    expected = "電話番号は[masked phone number]です。"
    assert mask_text(text) == expected
