#!/usr/bin/env python3
"""
Setup Ontos Demo Data via Direct Database Access

This script directly inserts demo data into the PostgreSQL database,
bypassing the API layer. Use with caution!

Usage:
    python demo/setup_ontos_db_direct.py --db-url postgresql://user:pass@host:5432/ontos
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
backend_path = Path(__file__).parent.parent / "src" / "backend" / "src"
sys.path.insert(0, str(backend_path))

from db_models.data_domains import DataDomainDb
from db_models.teams import TeamDb
from db_models.projects import ProjectDb
from common.database import Base


class DirectDatabaseSetup:
    """Setup demo data via direct database access."""

    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_domains(self):
        """Create data domains."""
        print("\n" + "=" * 80)
        print("Creating Data Domains (Direct DB)")
        print("=" * 80)

        session = self.SessionLocal()
        try:
            domains_data = [
                {
                    'name': 'Healthcare Core',
                    'description': 'Foundational healthcare concepts applicable across all business functions',
                    'tags': 'healthcare,enterprise,core',
                    'parent_domain_id': None
                },
                {
                    'name': 'Clinical',
                    'description': 'Clinical data including diagnoses, procedures, medications, and care events',
                    'tags': 'clinical,hipaa,phi',
                    'parent_domain_id': None  # Will be set after Healthcare Core is created
                },
                {
                    'name': 'Claims & Operations',
                    'description': 'Claims processing, provider networks, and operational data',
                    'tags': 'claims,operations,financial',
                    'parent_domain_id': None
                },
                {
                    'name': 'Member & Analytics',
                    'description': 'Member profiles, engagement data, and analytical insights',
                    'tags': 'member,analytics,engagement',
                    'parent_domain_id': None
                }
            ]

            created_domains = {}

            # Create Healthcare Core first
            hc_domain = DataDomainDb(
                id=str(uuid.uuid4()),
                name='Healthcare Core',
                description='Foundational healthcare concepts applicable across all business functions',
                tags='healthcare,enterprise,core',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(hc_domain)
            session.flush()
            created_domains['Healthcare Core'] = hc_domain.id
            print(f"  ✓ Created: Healthcare Core")

            # Create child domains
            for domain_data in domains_data[1:]:
                domain = DataDomainDb(
                    id=str(uuid.uuid4()),
                    name=domain_data['name'],
                    description=domain_data['description'],
                    tags=domain_data['tags'],
                    parent_domain_id=created_domains['Healthcare Core'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(domain)
                created_domains[domain_data['name']] = domain.id
                print(f"  ✓ Created: {domain_data['name']}")

            session.commit()
            print(f"\n✓ Created {len(created_domains)} domains")
            return created_domains

        except Exception as e:
            session.rollback()
            print(f"  ✗ Error: {e}")
            raise
        finally:
            session.close()

    def create_teams(self, domain_ids: dict):
        """Create teams."""
        print("\n" + "=" * 80)
        print("Creating Teams (Direct DB)")
        print("=" * 80)

        session = self.SessionLocal()
        try:
            teams_data = [
                {
                    'name': 'claims-engineering',
                    'title': 'Claims Data Engineering Team',
                    'domain_name': 'Claims & Operations',
                    'description': 'Responsible for claims data pipelines, EDI processing, and provider data integration',
                    'tags': 'claims,engineering,etl'
                },
                {
                    'name': 'member-analytics',
                    'title': 'Member Analytics Team',
                    'domain_name': 'Member & Analytics',
                    'description': 'Member experience analytics, segmentation, and engagement analysis',
                    'tags': 'analytics,member,reporting'
                },
                {
                    'name': 'clinical-data-science',
                    'title': 'Clinical Data Science Team',
                    'domain_name': 'Clinical',
                    'description': 'Predictive modeling for care management, risk adjustment, and utilization forecasting',
                    'tags': 'data-science,ml,clinical,predictive'
                },
                {
                    'name': 'governance-compliance',
                    'title': 'Data Governance & Compliance Team',
                    'domain_name': 'Healthcare Core',
                    'description': 'HIPAA compliance, data quality, and governance oversight',
                    'tags': 'governance,compliance,hipaa,quality'
                }
            ]

            created_teams = {}

            for team_data in teams_data:
                team = TeamDb(
                    id=str(uuid.uuid4()),
                    name=team_data['name'],
                    title=team_data['title'],
                    domain_id=domain_ids.get(team_data['domain_name']),
                    description=team_data['description'],
                    tags=team_data['tags'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(team)
                created_teams[team_data['name']] = team.id
                print(f"  ✓ Created: {team_data['name']}")

            session.commit()
            print(f"\n✓ Created {len(created_teams)} teams")
            return created_teams

        except Exception as e:
            session.rollback()
            print(f"  ✗ Error: {e}")
            raise
        finally:
            session.close()

    def create_projects(self, team_ids: dict):
        """Create projects."""
        print("\n" + "=" * 80)
        print("Creating Projects (Direct DB)")
        print("=" * 80)

        session = self.SessionLocal()
        try:
            projects_data = [
                {
                    'name': 'claims-modernization',
                    'title': 'Claims Processing Modernization',
                    'type': 'TEAM',
                    'owner_team': 'claims-engineering',
                    'description': 'Modernize claims processing pipeline from EDI 837/835 to real-time adjudication',
                    'tags': 'claims,modernization,automation'
                },
                {
                    'name': 'member-360',
                    'title': 'Member 360 Platform',
                    'type': 'TEAM',
                    'owner_team': 'member-analytics',
                    'description': 'Unified member data platform integrating claims, clinical, and engagement data',
                    'tags': 'member,platform,360-view'
                },
                {
                    'name': 'predictive-care-mgmt',
                    'title': 'Predictive Care Management',
                    'type': 'TEAM',
                    'owner_team': 'clinical-data-science',
                    'description': 'ML models for identifying high-risk members and reducing hospital readmissions',
                    'tags': 'ml,predictive,care-management,risk'
                }
            ]

            created_projects = {}

            for project_data in projects_data:
                project = ProjectDb(
                    id=str(uuid.uuid4()),
                    name=project_data['name'],
                    title=project_data['title'],
                    type=project_data['type'],
                    owner_team_id=team_ids.get(project_data['owner_team']),
                    description=project_data['description'],
                    tags=project_data['tags'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(project)
                created_projects[project_data['name']] = project.id
                print(f"  ✓ Created: {project_data['name']}")

            session.commit()
            print(f"\n✓ Created {len(created_projects)} projects")
            return created_projects

        except Exception as e:
            session.rollback()
            print(f"  ✗ Error: {e}")
            raise
        finally:
            session.close()

    def verify_setup(self):
        """Verify demo setup."""
        print("\n" + "=" * 80)
        print("Verifying Setup (Direct DB)")
        print("=" * 80)

        session = self.SessionLocal()
        try:
            domain_count = session.query(DataDomainDb).count()
            team_count = session.query(TeamDb).count()
            project_count = session.query(ProjectDb).count()

            print(f"\nDomains: {domain_count}")
            print(f"Teams: {team_count}")
            print(f"Projects: {project_count}")

            print("\n✓ Verification complete")

        finally:
            session.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Ontos demo data via direct database access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This script directly modifies the database, bypassing API validation.
         Use only when the API approach doesn't work or for development/testing.

Examples:
  # Using environment variable
  export DATABASE_URL="postgresql://user:pass@localhost:5432/ontos"
  python demo/setup_ontos_db_direct.py

  # Using command line
  python demo/setup_ontos_db_direct.py --db-url postgresql://user:pass@host:5432/ontos
        """
    )

    parser.add_argument(
        '--db-url',
        help='PostgreSQL database URL (or set DATABASE_URL env var)'
    )

    args = parser.parse_args()

    # Get database URL
    import os
    db_url = args.db_url or os.getenv('DATABASE_URL')

    if not db_url:
        print("❌ Error: Database URL not provided")
        print("   Set DATABASE_URL environment variable or use --db-url")
        sys.exit(1)

    print("=" * 80)
    print("Ontos Healthcare Payor Demo Setup (Direct DB Access)")
    print("=" * 80)
    print(f"\n⚠️  WARNING: Direct database access - bypasses API validation")
    print(f"Database: {db_url.split('@')[1] if '@' in db_url else db_url}")

    response = input("\nContinue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)

    try:
        setup = DirectDatabaseSetup(db_url)

        # Create entities
        domain_ids = setup.create_domains()
        team_ids = setup.create_teams(domain_ids)
        project_ids = setup.create_projects(team_ids)

        # Verify
        setup.verify_setup()

        print("\n" + "=" * 80)
        print("✓ Demo Setup Complete!")
        print("=" * 80)
        print("\nNote: Contracts and Products require API creation")
        print("      Use setup_ontos_demo.py for those")

    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
