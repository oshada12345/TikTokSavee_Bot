from TikTokApi import TikTokApi
verifyFp='xxx'
api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endpoints=True)
results = 10
hashtag = 'Messi'
search_results = api.by_hashtag(count=results, hashtag=hashtag)
for tiktok in search_results:
    print(tiktok['video']['playAddr'])