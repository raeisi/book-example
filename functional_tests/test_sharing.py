from selenium import webdriver
from .base import FunctionalTest
from .home_and_list_pages import HomePage

def quit_if_possible(browser):
    try: browser.quit()
    except: pass


class SharingTest(FunctionalTest):

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session('edith@email.com')
        edith_browser = self.browser
        self.addCleanup(lambda: quit_if_possible(edith_browser))

        # Oniciferous is also hanging out on the lists site
        oni_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser
        self.create_pre_authenticated_session('oniciferous@email.com')

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        HomePage(self).start_new_list('Get help')

        # She notices a "Share this list" option
        share_box = self.browser.find_element_by_css_selector('input[name=email]')
        self.assertEqual(
            share_box.get_attribute('placeholder'),
            'your@friends-email.com'
        )

        share_box.send_keys('oniciferous@email.com\n')

        # The page updates to say that it's shared with Oniciferous:
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Shared with', body_text)
        self.assertIn('oniciferous@email.com', body_text)

        # Oniciferous now goes to the 'My lists' page with his browser
        self.browser = oni_browser
        self.browser.get(self.server_url)
        self.browser.find_element_by_link_text('My lists').click()

        # He sees edith's list in there!
        self.browser.find_element_by_link_text('Get help').click()

        # It says that it's edith's list
        self.wait_for(
            lambda: self.assertIn(
                'List owner: edith@email.com',
                self.browser.find_element_by_tag_name('body').text
            )
        )

        # He adds an item to the list
        self.get_item_input_box().send_keys('Hi Edith!\n')

        # When edith refreshes the page, she sees Oniciferous's addition
        self.browser = edith_browser
        self.browser.refresh()
        self.check_for_row_in_list_table('2: Hi Edith!')

