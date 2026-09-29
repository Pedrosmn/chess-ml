SELECT
  CASE
    WHEN g < 50  THEN '0-49'
    WHEN g < 100 THEN '50-99'
    WHEN g < 200 THEN '100-199'
    WHEN g < 400 THEN '200-399'
    ELSE '400+'
  END AS faixa_gap,
  COUNT(*)        AS jogos,
  AVG(fl_upset)   AS taxa_zebra
FROM (
  SELECT uuid, MAX(fl_upset) AS fl_upset, MAX(ABS(elo_diff)) AS g
  FROM abt
  GROUP BY uuid
)
GROUP BY 1
ORDER BY MIN(g);