# mdBook Search GitHub Pages API generator

## Why and What for ?

You might have already encountered various communities offering tools or services and support for them via Discord. Most of them use bots and bot commands to answer the most common question. This works but has some limitations that I considered suboptimal especially for tools in active development and/or a very large userbase with the craziest variations in setups:

1. The typical bot commands can only be updated by the bot maintainers (Dyno Bot, etc)
2. It is easier for commands to become invalid and forgotten by maintainers when the app updates, due to developers and app users not always are part of the bot maintainer team (Managing specific Bots also has a learning curve not every developer wants to commit too, especially since those bots are always in development and things change with them as well)
3. Some projects are very big and need to split into different Discord servers which will all need to set up their own bots and maintain their custom tags as well manually causing more work and risk of outdated information.

**So how do I want to address this ? And how did we get here ?**

*Explained at the example project I build this for [Wabbajack Modlist Installer](https://wiki.wabbajack.org).*

1. Since our old documentation for years only consistet of: 
   - a big README.md (Note to self: find an old commit and link it statically here) not many people wanted to read due to its size
   - later partially in GitHubs own wiki functionality but not well searchable
   We decided to do something about it.
2. That something was setting up mdBook for our documentation and as a general wiki with everything an information about the tool and common troubleshooting steps. It comes with:
   - a very intuitive and easy to navigate interface (unlike GitHub, at least for most of the users that usually aren't involved with programming at all)
   - has a search function so people can search for errors and feature documentation **on the website**
   Now we have the users that want to look up their own solutions to their issues covered since they can just visit the website, but what about Discord.
3. To improve the support on the discord for people coming their for help we use(d) custom Dyno commands (triggers):
   - Pros:
     - frequent queries have a tag with an automated helpful response
   - Cons:
     - due to a lack of auto complete tags get forgotten and if not used outdated in cases they might get used again
     - even if they get used they are hard to update
     - it takes a lot of time to add new tags
     Those cons really make it so supporting users becomes a burden for everyone volunteering to do so and the information they can easily deliver sometimes is outdated, so what's the planned change ?
4. Making/Updating a bot capable to use the mbBook search for automatically generating wiki search results in discord to redirect users to the one place where all documentation should be accessed the mdBook based wiki. How:
   1. This workflow can generate "cached" json formatted files based on the queries listed in a json formatted queries.json.
   2. Adding a command that can auto complete to exist/cached queries or requests new queries if a fitting one doesn't exist using said queries.json file and delivering the json for an auto completeed query.
   With this the bot isn't as fast or dynamic as the direct use of the website search, BUT it is a lot easier to add new information or new tags compared to the old bot solution since the system will always link to the latest official documentation on the website instead of some old even more static code inside a discord bot. Also the idea is to implement this into a bot that any related server can add and with this system every server would also have access to the same cached queries via a single bot with nothing to do besides adding the bot properly and configure it to listen to the command in the right channels.

## Important Limitations of this workflow

1. Queries **only** work after they were cached.
2. This workflow is only useful if you know your tool or your Discord bot will be used to repeat frequent queries  about support questions (this is what this was made for).
3. You should use the queries.json to send a list to your tool/bot of pre-cached queries to avoid similar queries and use as many existing ones as possible.(Not mandatory but it will improve the user experience drastically since they don't have to wait until their new query got cached.)
4. The `raw.` links this tool relies on cache existing files for 5 minutes. So if a new query got added and then a regeneration was triggered that new query will take ~5minutes to update to the results of the updated website.
5. THIS IS STATIC AND SLOW!!
  - But it is so by design!

## Using this action

To use this action create or expand an existing workflow.yaml with the following implementations:

A dispatch workflow that can be triggered via the GitHub REST API:
Use case:

  - Push a new query to queries.json in the "POST" branch (ideally using the GitHub REST API)
  - Trigger the workflow on the main branch (manually or ideally using the GitHub REST API)

```yaml
name: Prepare Queries
on:
  push: 
    branches: [POST]
  workflow_dispatch:
jobs:
    get-num-square:
      runs-on: ubuntu-latest
      name: Testing functionality
      steps:
        - name: RUN PSEUDO-API Generator
          id: query_generator
          uses: EzioTheDeadPoet/mdBook_rawJSON_api_generator@1.0
          with:
            github_token: ${{ secrets.GITHUB_TOKEN }}
            mbBook_url: https://rust-lang.github.io/mdBook/
            api_repo: ${{ github.repository }}

```

Update your queries once a new mdBook got deployed with GitHub pages:

  - Only works if you use this in the same repository as your mdBook
  - this is the last workflow that runs that alters the deployment branch

```yaml
name: Regenerate Cache
on:
  workflow_run:
    workflows: ["pages-build-deployment"] 
    types:
      - completed
  workflow_dispatch:

jobs:
    get-num-square:
      runs-on: ubuntu-latest
      name: Testing functionality
      steps:
        - name: Run PSEUDO-API Generator
          id: query_generator
          uses: EzioTheDeadPoet/mdBook_rawJSON_api_generator@1.0
          with:
            github_token: ${{ secrets.GITHUB_TOKEN }}
            mbBook_url: https://rust-lang.github.io/mdBook/
            api_repo: ${{ github.repository }}
            regenerate_cache: "True"
```

Formatting and content of the queries.json on the GET branch:
```json
[
  {
    "query": "query1"
  },
  {
    "query": "query2"
  },
  {
    "query": "query3"
  },
  {
    "query": "query4"
  }
]
```
