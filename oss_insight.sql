SELECT
  gr.name as repository_name
FROM
  github_repos gr
  JOIN github_repo_topics grt ON gr.repo_id = grt.repo_id
WHERE
  gr.primary_language IN ('C', 'C++')
  AND gr.stars > 4000
  AND gr.forks > 1000
  AND gr.size > 2048
  AND gr.repo_id IN (
    SELECT
      repo_id
    FROM
      github_events
    WHERE
      type = 'PullRequestEvent'
      AND action = 'closed'
    GROUP BY repo_id
    HAVING COUNT(*) > 1000
  )
  AND gr.repo_id IN (
    SELECT
      repo_id
    FROM
      github_events
    WHERE
      type = 'PullRequestEvent'
      AND action = 'closed'
    GROUP BY repo_id
    HAVING COUNT(DISTINCT creator_user_login) > 100
  )