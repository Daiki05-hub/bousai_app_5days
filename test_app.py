import unittest

from app import app, parse_area_warnings


class ShelterAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.secret_key = 'test-secret-key'

    def test_login_accepts_username_and_password(self):
        response = self.client.post('/login', data={'username': 'admin', 'password': '123'}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/shelter_register')

    def test_shelter_registration_saves_new_shelter(self):
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'

        response = self.client.post('/shelter_register', data={'name': 'テスト避難所'}, follow_redirects=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn('テスト避難所', response.get_data(as_text=True))

    def test_parse_area_warnings_uses_aomori_city_code(self):
        sample = [{
            'reportDatetime': '2026-09-02T11:17:00+09:00',
            'warning': {
                'class20Items': [{
                    'areaCode': '0240100',
                    'kinds': [{'code': '43', 'status': '継続'}]
                }]
            }
        }]

        warnings, report_datetime = parse_area_warnings(sample)
        self.assertEqual(report_datetime, '2026-09-02T11:17:00+09:00')
        self.assertEqual(warnings[0]['code'], '43')
        self.assertEqual(warnings[0]['name'], 'レベル4大雨危険警報')

    def test_home_page_uses_aomori_city_name(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('青森市', response.get_data(as_text=True))
        self.assertNotIn('藤沢市', response.get_data(as_text=True))

    def test_board_post_saves_content_and_meta(self):
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'admin'

        response = self.client.post('/board', data={
            'content': '避難してください',
            'posted_at': '2026-08-03T14:23',
            'district': 'A地区',
            'priority': '大',
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)

        page = self.client.get('/board')
        html = page.get_data(as_text=True)
        self.assertIn('避難してください', html)
        self.assertIn('A地区', html)
        self.assertIn('大', html)


if __name__ == '__main__':
    unittest.main()
