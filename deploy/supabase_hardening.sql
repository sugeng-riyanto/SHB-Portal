-- SHB Portal: harden Django-created tables against Supabase Data API access.
-- REVIEW ONLY: run after Django migrations on a dedicated staging project,
-- never an existing shared project without a full review and backup.
-- RLS here is deny-by-default: it intentionally provides NO client policies.
-- Django's direct DB role may bypass RLS and MUST enforce authorization itself.
-- This script does not configure Supabase Auth or make the app production-ready.
BEGIN;
DO $$
DECLARE
    table_name text;
    expected_tables text[] := ARRAY[
        'portal_school', 'portal_membership', 'portal_academicyear',
        'portal_classroom', 'portal_classroom_teachers', 'portal_student',
        'portal_student_guardians', 'portal_enrollment', 'portal_invoice',
        'portal_payment', 'portal_schoolannouncement', 'portal_paymentreceipt', 'portal_paymenttype', 'portal_activityevent', 'portal_proofcomment', 'portal_integrationconfig', 'portal_schoolupdate', 'portal_userprofile', 'portal_message', 'portal_bankaccount', 'portal_transferproof', 'auth_user', 'auth_user_groups',
        'auth_user_user_permissions', 'auth_group', 'auth_group_permissions',
        'auth_permission', 'django_session', 'django_admin_log',
        'django_content_type', 'django_migrations'
    ];
BEGIN
    -- Check everything before mutating anything. The transaction rolls back on error.
    FOREACH table_name IN ARRAY expected_tables LOOP
        IF to_regclass(format('public.%I', table_name)) IS NULL THEN
            RAISE EXCEPTION 'Missing public table %, run Django migrations first on the intended database', table_name;
        END IF;
    END LOOP;
    FOREACH table_name IN ARRAY expected_tables LOOP
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('REVOKE ALL ON TABLE public.%I FROM PUBLIC, anon, authenticated', table_name);
    END LOOP;
END $$;
COMMIT;
