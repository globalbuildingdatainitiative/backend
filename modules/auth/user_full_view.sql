CREATE OR REPLACE VIEW user_full_view AS
SELECT 
    e.user_id,
    e.email,
    e.time_joined,
    m.user_metadata::jsonb AS metadata,
    l.last_active_time,
    array_agg(r.role) AS roles
FROM emailpassword_users e
LEFT JOIN user_metadata m ON e.user_id = m.user_id
LEFT JOIN user_last_active l ON e.user_id = l.user_id
LEFT JOIN user_roles r ON e.user_id = r.user_id
GROUP BY e.user_id, e.email, e.time_joined, m.user_metadata, l.last_active_time;
