# Social Watcher
![maintain status](https://img.shields.io/maintenance/yes/2020)


**Social Watchers** allows you to watch and record changes on Twitter and Instagram accounts. It can alert you the changes via Telegram.


## Prerequisites
Before you begin, ensure you have met the following requirements:

* Internet Connection
* Python 3.7+

## Installing social-watcher

First, clone repository to local and install requirements. You can install requirements with ```pip3 install -r requirements.txt```. <br />
Then you need to edit *configs.json.example* as you wish and rename it to *configs.json*. At the end you can run *watcher.py*


## Metrics

List of metrics which one watching.

| Platform  | Metrics                                                                                |
|-----------|----------------------------------------------------------------------------------------|
| Twitter   | name, followers, following, biography, profile_photo, tweets, likes, birthday, website |
| Instagram | name, followers, following, biography, profile_photo, posts, is_private, is_verified   |

## Customizing Configs

```json
{
    "interval": 300, # general interval time, default is 86400 (1 day)

    "telegram": {
        "token": "9999999999:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", # telegram bot token
        "chat_id": "999999999" # telegram chat id
    },

    "instagram": [
        {
            "username": "bisguzar", # username, required

            "interval": 5, # interval for this watcher as seconds
                           # if not defined it uses general interval

            "only_if_changed": false, # not required
                                      # if false it will report you if no changes
                                      # default is true

            "ignored_metrics": ["profile_photo"] # not required, 
                                                 # it will ignore this metrics even is changed
        },
        {...another instagram watcher...},
        {...another instagram watcher...}
    ],

    "twitter": [
        {
            "username": "bugraisguzar", # username, required
            
            "interval": 30, # interval for this watcher as seconds
                            # if not defined it uses general interval

            "only_if_changed": false, # not required
                                      # if false it will report you if no changes
                                      # default is true

            "ignored_metrics": ["likes"] # not required, 
                                                 # it will ignore this metrics even is changed
        },
        {...another twitter watcher...},
        {...another twitter watcher...}
    ]
}
```


## Contributing to social-watcher
To contribute to twitter-scraper, follow these steps:

1. Fork this repository.
2. Create a branch with clear name: `git checkout -b <branch_name>`.
3. Make your changes and commit them: `git commit -m '<commit_message>'`
4. Push to the original branch: `git push origin <project_name>/<location>`
5. Create the pull request.

Alternatively see the GitHub documentation on [creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request).

## Contributors

* @bisguzar


## Contact
If you want to contact me you can reach me at [@bugraisguzar](https://twitter.com/bugraisguzar).


## License
This project uses the following license: [MIT](https://github.com/bisguzar/twitter-scraper/blob/master/LICENSE).
