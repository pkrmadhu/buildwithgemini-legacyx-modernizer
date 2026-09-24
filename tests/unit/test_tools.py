# Copyright 2026 Google LLC
# Unit tests for LegacyX Modernizer tools

from app.agent import (
    analyze_tech_stack,
    recommend_modern_stack,
    modernize_code_file,
    generate_migration_roadmap,
    generate_unit_tests,
    modernize_database_layer,
    verify_and_repair_code,
    verify_dual_behavior_safety,
)


def test_analyze_tech_stack():
    snippet = "Struts 1.2, javax.servlet, Java 8, EJB 2.1"
    res = analyze_tech_stack(snippet)
    assert res["status"] == "success"
    assert "Apache Struts 1.x / 2.x" in res["detected_legacy_stack"]
    assert "EJB (Enterprise JavaBeans 2.x/3.x)" in res["detected_legacy_stack"]
    assert res["technical_debt_risk_score"] == "72/100"


def test_recommend_modern_stack():
    res = recommend_modern_stack("Struts")
    assert res["legacy_technology"] == "Struts"
    assert "Spring Boot 3" in res["target_modern_stack"]
    assert len(res["key_upgrades"]) > 0


def test_modernize_code_file():
    res = modernize_code_file("UserService.java", "public class UserService {}", "Spring Boot 3 + Java 21")
    assert res["status"] == "success"
    assert res["file_name"] == "UserService.java"
    assert res["modernized_file_name"] == "ModernUserService.java"
    assert "use.modern.user" in res["modernized_code"]
    assert "FeatureToggleService" in res["modernized_code"]


def test_generate_migration_roadmap():
    res = generate_migration_roadmap("MonolithApp", "Java 8 EJB", "Spring Boot 3")
    assert res["project_name"] == "MonolithApp"
    assert len(res["migration_phases"]) == 5
    assert res["migration_phases"][0]["name"] == "Discovery & Codebase Inspection"


def test_generate_unit_tests():
    res = generate_unit_tests("UserService.java", "public class UserService {}", "public class ModernUserService {}")
    assert res["status"] == "success"
    assert res["test_class_name"] == "ModernUserServiceTest.java"
    assert "JUnit 5" in res["test_framework"]
    assert "@Test" in res["unit_test_code"]
    assert "testProcessRequest_WhenFeatureFlagEnabled_ExecutesModernPath" in res["unit_test_code"]


def test_modernize_database_layer():
    legacy_sql = "SELECT * FROM users WHERE user_id = ?"
    res = modernize_database_layer(legacy_sql)
    assert res["status"] == "success"
    assert "UserEntity.java" in res["components_generated"][0]
    assert "@Entity" in res["jpa_entity_code"]
    assert "JpaRepository" in res["jpa_repository_code"]
    assert "CREATE TABLE" in res["flyway_migration_sql"]


def test_verify_and_repair_code():
    unclean_code = "import javax.servlet.http.HttpServletRequest;\npublic class OrderService {}"
    res = verify_and_repair_code(unclean_code)
    assert res["status"] == "success"
    assert res["is_valid"] is True
    assert "jakarta.servlet" in res["repaired_code"]
    assert "@org.springframework.stereotype.Service" in res["repaired_code"]


def test_verify_dual_behavior_safety():
    res = verify_dual_behavior_safety("UserService")
    assert res["status"] == "success"
    assert res["feature_flag_key"] == "use.modern.userservice"
    assert len(res["canary_rollout_strategy"]) == 3
    assert len(res["automated_rollback_triggers"]) > 0
