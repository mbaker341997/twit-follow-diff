import requests_mock
from flaskr.follow_diff import *

TEST_USER = "dummy_user"
TEST_FOLLOWERS = {'ids': ['1', '2']}
TEST_FRIENDS = {'ids': ['2', '3', '4']}
TEST_HATERS_DATA = {'data': [
    {
        'id': '3',
        'profile_image_url': 'https://foo.com/image_normal.jpg',
        'name': 'Test User 3',
        'username': 'test_user_3',
        'description': 'This is a test user. Linkifies https://foo.com/'
    },
    {
        'id': '4',
        'profile_image_url': 'https://bar.com/image_normal.jpg',
        'name': 'Test User 4',
        'username': 'test_user_4',
        'description': 'this is another test user. Username linkifies @test_user_3 but not email@fake.com'
    }
]}
TEST_VICTIM_DATA = {'data': [
    {
        'id': '1',
        'profile_image_url': 'https://fake.com/image_normal.jpg',
        'name': 'Test User 1',
        'username': 'test_user_1',
        'description': 'This is a test user. Linkifies https://foo.com/'
    }
]}


def test_index(client):
    response = client.get('/')
    assert_page_top(response.data)
    assert_no_query_param_errors(response.data)
    assert_no_cards(response.data)


def test_diff_no_params_returns_errors(client):
    response = client.get('/diff')
    assert_page_top(response.data)

    # two errors, one for no username, the other for no type
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) in response.data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) in response.data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) not in response.data

    # no cards
    assert_no_cards(response.data)


def test_diff_invalid_account_type_returns_error(client):
    response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, 'invalidType'))
    assert_page_top(response.data)

    # only an error for invalid type
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) not in response.data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) not in response.data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) in response.data

    # no cards
    assert_no_cards(response.data)


def test_simple_diff_haters(client):
    with requests_mock.Mocker() as mock_request:
        # 1 and 2 follow test user
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json=TEST_FOLLOWERS)

        # test user follows 2, 3, and 4
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json=TEST_FRIENDS)

        # We're looking for haters, people who don't follow us back, so we should only be retrieving data for 3 and 4
        mock_request.get(USER_INFO_API_URL.format('3,4'), json=TEST_HATERS_DATA)

        # Order of ids chunk isn't consistent in the set difference.
        # I don't want to add sorting logic just for the tests
        # Regex might work I guess, but requests-mock involved an adapter for that, this seemed easier.
        mock_request.get(USER_INFO_API_URL.format('4,3'), json=TEST_HATERS_DATA)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, HATERS_TYPE))
        assert_page_top(response.data)

        # no errors
        assert_no_query_param_errors(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers, and 1 for the data
        assert mock_request.call_count == 3
        # account metrics
        assert_account_metrics(response.data, followers_count=2, followed_count=3, haters_count=2, victims_count=1)
        # card for 3
        assert_card_correct(response.data, '3', 'https://foo.com/image.jpg', 'test_user_3', 'Test User 3',
                            'This is a test user. Linkifies <a href="https://foo.com/" rel="nofollow">'
                            'https://foo.com/</a>')
        # card for 4
        assert_card_correct(response.data, '4', 'https://bar.com/image.jpg', 'test_user_4', 'Test User 4',
                            'this is another test user. Username linkifies '
                            '<a href="https://twitter.com/test_user_3">@test_user_3</a> but not email@fake.com')


def test_simple_diff_victims(client):
    with requests_mock.Mocker() as mock_request:
        # 1 and 2 follow test user
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json=TEST_FOLLOWERS)

        # test user follows 2, 3, and 4
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json=TEST_FRIENDS)

        # We're looking for victims, people we don't follow back, so we should only be retrieving data for 1
        mock_request.get(USER_INFO_API_URL.format('1'), json=TEST_VICTIM_DATA)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # no errors
        assert_no_query_param_errors(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers, and 1 for the data
        assert mock_request.call_count == 3
        # account metrics
        assert_account_metrics(response.data, followers_count=2, followed_count=3, haters_count=2, victims_count=1)
        # card for 1
        assert_card_correct(response.data, '1', 'https://fake.com/image.jpg', 'test_user_1', 'Test User 1',
                            'This is a test user. Linkifies <a href="https://foo.com/" rel="nofollow">'
                            'https://foo.com/</a>')


def test_too_many_friends(client):
    with requests_mock.Mocker() as mock_request:
        # 1 and 2 follow test user
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json=TEST_FOLLOWERS)

        # test user follows too many accounts
        friends_id_list = ["{}".format(x) for x in range(2, 5002)]
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json={'ids': friends_id_list})

        # We're looking for victims, people we don't follow back, so we should only be retrieving data for 1
        mock_request.get(USER_INFO_API_URL.format('1'), json=TEST_VICTIM_DATA)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # no errors with query params
        assert_no_query_param_errors(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers, and 1 for the data
        assert mock_request.call_count == 3
        # account metrics
        assert_account_metrics(response.data, followers_count=2, followed_count=5000, haters_count=4999,
                               victims_count=1)
        # too many follows error message
        assert str.encode(TOO_MANY_FOLLOWS_ERROR_MESSAGE) in response.data
        # card for 1
        assert_card_correct(response.data, '1', 'https://fake.com/image.jpg', 'test_user_1', 'Test User 1',
                            'This is a test user. Linkifies <a href="https://foo.com/" rel="nofollow">'
                            'https://foo.com/</a>')


def test_too_many_followers(client):
    with requests_mock.Mocker() as mock_request:
        # test user has too many followers
        followers_id_list = ["{}".format(x) for x in range(0, 5000)]
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json={"ids": followers_id_list})

        # test user follows 2, 3, and 4. Notice: we have no haters
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json=TEST_FRIENDS)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, HATERS_TYPE))
        assert_page_top(response.data)

        # no errors with query params
        assert_no_query_param_errors(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers
        assert mock_request.call_count == 2
        # account metrics
        assert_account_metrics(response.data, followers_count=5000, followed_count=3, haters_count=0,
                               victims_count=4997)
        # too many follows error message
        assert str.encode(TOO_MANY_FOLLOWERS_ERROR_MESSAGE) in response.data

        # no cards. everyone we follow is in our followers list
        assert_no_cards(response.data)


def test_not_authorized_for_user(client):
    with requests_mock.Mocker() as mock_request:
        # trying to get followers returns a 401 status code
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), status_code=401)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # we have the username and valid account type, it was twitter that told us this username was bad
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        # only should have made 1 request, for followers
        assert mock_request.call_count == 1
        assert str.encode(NOT_AUTHORIZED_FOR_USER_TEMPLATE.format(FOLLOWERS_KEY, TEST_USER)) in response.data


def test_user_not_found_by_twitter(client):
    with requests_mock.Mocker() as mock_request:
        # trying to get followers returns a 401 status code
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), status_code=404)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # we have the username and valid account type, it was twitter that told us this username was bad
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        # only should have made 1 request, for followers
        assert mock_request.call_count == 1
        assert str.encode(USER_NOT_FOUND_TEMPLATE.format(TEST_USER)) in response.data


def test_rate_limit_on_account_list_retrieval(client):
    with requests_mock.Mocker() as mock_request:
        # trying to get followers returns a 401 status code
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), status_code=429)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # we have the username and valid account type, it was twitter that told us this username was bad
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        # only should have made 1 request, for followers
        assert mock_request.call_count == 1
        assert str.encode(RATE_LIMIT_ON_ACCOUNT_LIST_TEMPLATE.format(FOLLOWERS_KEY, TEST_USER)) in response.data


def test_random_error_on_account_list_retrieval(client):
    with requests_mock.Mocker() as mock_request:
        # trying to get followers returns a 401 status code
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), status_code=500, text="Some error")

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # we have the username and valid account type, it was twitter that told us this username was bad
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        print(response.data)

        # only should have made 1 request, for followers
        assert mock_request.call_count == 1
        assert str.encode(GENERIC_ERROR_MESSAGE_FOR_FRONTEND) in response.data


def test_rate_limit_on_user_info_retrieval(client):
    with requests_mock.Mocker() as mock_request:
        # 1 and 2 follow test user
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json=TEST_FOLLOWERS)

        # test user follows 2, 3, and 4
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json=TEST_FRIENDS)

        # We're looking for victims, people we don't follow back, so we should only be retrieving data for 1
        mock_request.get(USER_INFO_API_URL.format('1'), status_code=429)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # no errors
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers, and 1 for the data
        assert mock_request.call_count == 3
        assert str.encode(RATE_LIMIT_ON_USER_INFO_MESSAGE) in response.data


def test_random_error_on_user_info_retrieval(client):
    with requests_mock.Mocker() as mock_request:
        # 1 and 2 follow test user
        mock_request.get(ACCOUNT_LIST_API_URL.format(FOLLOWERS_KEY, TEST_USER), json=TEST_FOLLOWERS)

        # test user follows 2, 3, and 4
        mock_request.get(ACCOUNT_LIST_API_URL.format(FRIENDS_KEY, TEST_USER), json=TEST_FRIENDS)

        # We're looking for victims, people we don't follow back, so we should only be retrieving data for 1
        mock_request.get(USER_INFO_API_URL.format('1'), status_code=500)

        response = client.get('/diff?{}={}&{}={}'.format(USERNAME_KEY, TEST_USER, TYPE_KEY, VICTIMS_TYPE))
        assert_page_top(response.data)

        # no errors
        assert_no_query_param_errors(response.data)

        # no cards rendered
        assert_no_cards(response.data)

        # only should have made 3 requests. 1 for friends, 1 for followers, and 1 for the data
        assert mock_request.call_count == 3
        assert str.encode(GENERIC_ERROR_MESSAGE_FOR_FRONTEND) in response.data


def assert_page_top(response_data):
    # Make sure we have the main ideas -> explanation of what the app is and the username input
    # response.data returns bytes so compare bytes to bytes
    assert b'TwitDiff' in response_data
    assert b'See who doesn\'t follow you back.' in response_data
    assert b'Also see who you don\'t follow back.' in response_data
    assert b'<input name="username"' in response_data


def assert_account_metrics(response_data, followers_count, followed_count, haters_count, victims_count):
    assert str.encode('Total Followers: {}'.format(followers_count)) in response_data
    # 3 total followed accounts
    assert str.encode('Total Followed Accounts: {}'.format(followed_count)) in response_data
    # 2 you follow but they don't follow back
    assert str.encode('Total you follow but they don\'t follow back: {}'.format(haters_count)) in response_data
    # 1 who follows you but you don't follow back
    assert str.encode('Total that follow you but you don\'t follow back: {}'.format(victims_count)) in response_data


def assert_card_correct(response_data, account_id, account_image, account_username, account_name, account_description):
    # div for card with account's id as its id
    assert str.encode('<div class="card m-4" id={}>'.format(account_id)) in response_data
    # profile image
    assert str.encode('<img src="{}" class="card-img-top" alt={}>'.format(account_image, account_username)) \
           in response_data
    # account name title
    assert str.encode('<h5>{}</h5>'.format(account_name)) in response_data
    # account username link
    assert str.encode('<a href="https://twitter.com/{}">@{}</a>'.format(account_username, account_username)) \
           in response_data
    # card text
    assert str.encode('<p class="card-text"> {} </p>'.format(account_description)) in response_data


def assert_no_cards(response_data):
    assert b'card' not in response_data
    assert b'card-img-top' not in response_data
    assert b'card-body' not in response_data
    assert b'card-text' not in response_data


# Errors due to missing query params, or bad account type. You should have known better
def assert_no_query_param_errors(response_data):
    assert str.encode(MISSING_USERNAME_ERROR_MESSAGE) not in response_data
    assert str.encode(MISSING_TYPE_ERROR_MESSAGE) not in response_data
    assert str.encode(INVALID_ACCOUNT_TYPE_ERROR_MESSAGE) not in response_data
