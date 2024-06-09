COMP_POSTS_QUERY = """
query categoryTopicList($categories: [String!]!, $first: Int!, $orderBy: TopicSortingOption, $skip: Int, $query: String, $tags: [String!]) {
  categoryTopicList(categories: $categories, orderBy: $orderBy, skip: $skip, query: $query, first: $first, tags: $tags) {
    ...TopicsList
    __typename
  }
}

fragment TopicsList on TopicConnection {
  totalNum
  edges {
    node {
      id
      title
      commentCount
      viewCount
      pinned
      tags {
        name
        slug
        __typename
      }
      post {
        id
        voteCount
        creationDate
        isHidden
        author {
          username
          isActive
          nameColor
          activeBadge {
            displayName
            icon
            __typename
          }
          profile {
            userAvatar
            __typename
          }
          __typename
        }
        status
        coinRewards {
          ...CoinReward
          __typename
        }
        __typename
      }
      lastComment {
        id
        post {
          id
          author {
            isActive
            username
            __typename
          }
          peek
          creationDate
          __typename
        }
        __typename
      }
      __typename
    }
    cursor
    __typename
  }
  __typename
}

fragment CoinReward on ScoreNode {
  id
  score
  description
  date
  __typename
}
"""


COMP_POSTS_DATA_QUERY = {
    "operationName": "categoryTopicList",
    "query": COMP_POSTS_QUERY,
    "variables": {
        "orderBy": "newest_to_oldest",
        "query": "",
        "skip": 0,
        "first": 50,
        "tags": [],
        "categories": ["compensation"],
    },
}


COMP_POST_CONTENT_QUERY = """
query DiscussTopic($topicId: Int!) {
  topic(id: $topicId) {
    id
    viewCount
    topLevelCommentCount
    subscribed
    title
    pinned
    tags
    hideFromTrending
    post {
      ...DiscussPost
      __typename
    }
    __typename
  }
}

fragment DiscussPost on PostNode {
  id
  voteCount
  voteStatus
  content
  updationDate
  creationDate
  status
  isHidden
  coinRewards {
    ...CoinReward
    __typename
  }
  author {
    isDiscussAdmin
    isDiscussStaff
    username
    nameColor
    activeBadge {
      displayName
      icon
      __typename
    }
    profile {
      userAvatar
      reputation
      __typename
    }
    isActive
    __typename
  }
  authorIsModerator
  isOwnPost
  __typename
}

fragment CoinReward on ScoreNode {
  id
  score
  description
  date
  __typename
}
"""


COMP_POST_CONTENT_DATA_QUERY = {
    "operationName": "DiscussTopic",
    "query": COMP_POST_CONTENT_QUERY,
    "variables": {"topicId": 0},
}
