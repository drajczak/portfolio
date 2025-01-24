-- Time interval settings
SET @start_date = '2025-01-13 00:00:00'; 
SET @end_date = '2025-01-17 00:00:00'; 

# Sales support
SELECT
    e.employees_collection AS worker,
	COUNT(*) AS sum,
    ROUND(COUNT(*) / 
    CASE
        WHEN `added_by_employee_id` LIKE '%k.ko%' THEN 5
        WHEN `added_by_employee_id` LIKE '%p.kucz%' THEN 5
		WHEN `added_by_employee_id` LIKE '%n.kwia%' THEN 5
        ELSE 5 -- default devisor
    END, 1) AS 'daily',
    e.event_type_id AS type

FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id

WHERE
    (
        (e.event_type_id = 'offer' OR e.event_type_id = 'VISIT' OR e.event_type_id = 'contact' OR e.event_type_id = "note")
        AND (e.employees_collection LIKE '%k.ko%' OR e.employees_collection LIKE '%p.kucz%' OR e.employees_collection LIKE '%n.kwia%') 
        AND e.event_date BETWEEN @start_date AND @end_date
    ) 

GROUP BY e.employees_collection, e.event_type_id
ORDER BY e.employees_collection, e.event_type_id
;

#sales team
SELECT COUNT(*) as 'salesmen records', ROUND(COUNT(*)/5, 1) AS 'daily salesmen records', `added_by_employee_id` as 'added by'
FROM crm.clients c
INNER JOIN crm.events e ON c.client_id = e.client_id
WHERE e.event_type_id LIKE '%%'

     AND (
 	(`added_by_employee_id` LIKE '%k.ko%' AND employees_collection NOT LIKE '%k.ko%')
     OR
     (`added_by_employee_id` LIKE '%p.kucz%' AND employees_collection NOT LIKE '%p.kucz%')
	OR
     (`added_by_employee_id` LIKE '%n.kw%' AND employees_collection NOT LIKE '%n.kw%'))

AND e.event_date BETWEEN @start_date AND @end_date
GROUP BY `added_by_employee_id`
ORDER BY e.employees_collection, e.event_type_id
;