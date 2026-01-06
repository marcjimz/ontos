#!/usr/bin/env python3
"""
Setup Ontos Demo Data via REST API

This script programmatically creates all demo entities (domains, teams, projects,
contracts, products) by calling the Ontos REST API endpoints.

Usage:
    # Local development
    python demo/setup_ontos_demo.py --base-url http://localhost:8000

    # Databricks App (requires databricks CLI configured)
    python demo/setup_ontos_demo.py \
      --base-url https://app-name.aws.databricksapps.com \
      --databricks-profile e2-demo-field-eng
"""

import requests
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, Any, List


class OntosSetup:
    """Setup Ontos demo data via REST API."""

    def __init__(self, base_url: str, databricks_profile: str = None, fail_fast: bool = True):
        self.base_url = base_url.rstrip('/')
        self.fail_fast = fail_fast
        self.error_count = 0
        self.databricks_profile = databricks_profile
        self.session = requests.Session()

        # Get identity token if using Databricks profile
        if databricks_profile:
            print(f"  Getting identity token for profile: {databricks_profile}")
            try:
                import subprocess
                result = subprocess.run(
                    ['databricks', 'auth', 'token', '--profile', databricks_profile],
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Parse JSON output to get access_token
                token_data = json.loads(result.stdout)
                self.identity_token = token_data['access_token']
                print(f"  ✓ Got identity token")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ Failed to get identity token: {e.stderr}")
                print(f"\n  Make sure you've configured the profile:")
                print(f"    databricks auth login --profile {databricks_profile}")
                sys.exit(1)
            except FileNotFoundError:
                print("  ✗ databricks CLI not found")
                print("     Install with: pip install databricks-cli")
                sys.exit(1)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  ✗ Failed to parse token response: {e}")
                sys.exit(1)
        else:
            self.identity_token = None

        # Will store created entity IDs
        self.domain_ids = {}
        self.team_ids = {}
        self.project_ids = {}
        self.contract_ids = {}
        self.product_ids = {}

    def _make_request(self, method: str, path: str, **kwargs):
        """Make an authenticated HTTP request."""
        url = f"{self.base_url}{path}"

        # Add identity token if using Databricks profile
        if self.identity_token:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.identity_token}'

        return self.session.request(method, url, **kwargs)

    def check_health(self) -> bool:
        """Verify backend is accessible."""
        print("\nChecking backend health...")

        # Try common health check endpoints
        health_endpoints = [
            "/api/version",  # Try version endpoint first (defined in app.py)
            "/health",
            "/api/health",
            "/",
        ]

        for endpoint in health_endpoints:
            try:
                response = self._make_request('GET', endpoint, timeout=10)
                status = response.status_code

                print(f"  Tried {self.base_url}{endpoint} -> {status}")

                # Show response preview for debugging
                if hasattr(response, 'text'):
                    preview = response.text[:200] if response.text else "(empty)"
                    print(f"    Response preview: {preview[:100]}...")

                if status in [200, 404]:  # 200 = success, 404 = backend exists but route not found
                    print(f"  ✓ Backend accessible at: {self.base_url}")
                    return True
                elif status in [401, 403]:
                    print(f"  ⚠ Backend accessible but authentication issue (HTTP {status})")
                    return True  # Backend is running, auth issue will be handled later

            except Exception as e:
                print(f"  Error on {endpoint}: {type(e).__name__}: {str(e)[:100]}")
                continue

        print(f"\n  ✗ Backend not accessible at: {self.base_url}")
        return False

    def _handle_error(self, action: str, url: str, response: requests.Response) -> None:
        """Handle API errors with better messaging."""
        self.error_count += 1

        print(f"  ✗ Failed: {response.status_code}")
        print(f"     URL: {url}")

        # Try to parse error message
        try:
            error_data = response.json()
            if 'detail' in error_data:
                print(f"     Detail: {error_data['detail']}")
        except:
            if response.text:
                print(f"     Response: {response.text[:200]}")

        if self.fail_fast:
            print(f"\n❌ Stopping due to error. Use --no-fail-fast to continue on errors.")
            sys.exit(1)

    def load_yaml_file(self, path: str) -> Any:
        """Load YAML file."""
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def create_domains(self, domains_config: List[Dict]) -> None:
        """Create data domains."""
        print("\n" + "=" * 80)
        print("Creating Data Domains")
        print("=" * 80)

        for domain in domains_config:
            print(f"\nCreating domain: {domain['name']}")

            # Resolve parent domain ID if specified
            if 'parent_domain' in domain and domain['parent_domain']:
                domain['parent_domain_id'] = self.domain_ids.get(domain['parent_domain'])

            response = self._make_request('POST', '/api/data-domains', json=domain)

            if response.status_code in [200, 201]:
                result = response.json()
                self.domain_ids[domain['name']] = result.get('id') or result.get('name')
                print(f"  ✓ Created: {domain['name']}")
            else:
                self._handle_error("create domain", f"{self.base_url}/api/data-domains", response)

    def create_teams(self, teams_config: List[Dict]) -> None:
        """Create teams."""
        print("\n" + "=" * 80)
        print("Creating Teams")
        print("=" * 80)

        for team in teams_config:
            print(f"\nCreating team: {team['name']}")

            response = self._make_request('POST', '/api/teams', json=team)

            if response.status_code in [200, 201]:
                result = response.json()
                self.team_ids[team['name']] = result.get('id') or result.get('name')
                print(f"  ✓ Created: {team['name']}")
            else:
                self._handle_error("create team", f"{self.base_url}/api/teams", response)

    def create_projects(self, projects_config: List[Dict]) -> None:
        """Create projects."""
        print("\n" + "=" * 80)
        print("Creating Projects")
        print("=" * 80)

        for project in projects_config:
            print(f"\nCreating project: {project['name']}")

            response = self._make_request('POST', '/api/projects', json=project)

            if response.status_code in [200, 201]:
                result = response.json()
                self.project_ids[project['name']] = result.get('id') or result.get('name')
                print(f"  ✓ Created: {project['name']}")
            else:
                self._handle_error("create project", f"{self.base_url}/api/projects", response)

    def create_contracts(self, contracts_dir: str) -> None:
        """Create data contracts from YAML files."""
        print("\n" + "=" * 80)
        print("Creating Data Contracts")
        print("=" * 80)

        contracts_path = Path(contracts_dir)
        if not contracts_path.exists():
            print(f"  ⚠ Contracts directory not found: {contracts_dir}")
            return

        for yaml_file in contracts_path.glob("*.yaml"):
            print(f"\nLoading contract: {yaml_file.name}")

            contract_data = self.load_yaml_file(yaml_file)

            response = self._make_request('POST', '/api/data-contracts', json=contract_data)

            if response.status_code in [200, 201]:
                result = response.json()
                contract_id = result.get('id')
                contract_name = contract_data.get('name')
                self.contract_ids[contract_name] = contract_id
                print(f"  ✓ Created: {contract_name} (ID: {contract_id})")
            else:
                self._handle_error("create contract", f"{self.base_url}/api/data-contracts", response)

    def create_products(self, products_file: str) -> None:
        """Create data products from YAML file."""
        print("\n" + "=" * 80)
        print("Creating Data Products")
        print("=" * 80)

        if not Path(products_file).exists():
            print(f"  ⚠ Products file not found: {products_file}")
            return

        products_data = self.load_yaml_file(products_file)

        if not isinstance(products_data, list):
            products_data = [products_data]

        for product in products_data:
            print(f"\nCreating product: {product.get('name', 'Unknown')}")

            # Remove tags field if it exists - tags should be added after creation
            # The YAML has simple string tags but API expects AssignedTag objects
            if 'tags' in product:
                del product['tags']

            # Also remove tags from nested structures
            for port in product.get('inputPorts', []):
                if 'tags' in port:
                    del port['tags']
            for port in product.get('outputPorts', []):
                if 'tags' in port:
                    del port['tags']

            response = self._make_request('POST', '/api/data-products', json=product)

            if response.status_code in [200, 201]:
                result = response.json()
                product_id = result.get('id')
                product_name = product.get('name')
                self.product_ids[product_name] = product_id
                print(f"  ✓ Created: {product_name} (ID: {product_id})")
            else:
                self._handle_error("create product", f"{self.base_url}/api/data-products", response)

    def verify_setup(self) -> None:
        """Verify demo setup by checking entity counts."""
        print("\n" + "=" * 80)
        print("Verifying Setup")
        print("=" * 80)

        checks = [
            ("Domains", f"{self.base_url}/api/data-domains", self.domain_ids),
            ("Teams", f"{self.base_url}/api/teams", self.team_ids),
            ("Projects", f"{self.base_url}/api/projects", self.project_ids),
            ("Contracts", f"{self.base_url}/api/data-contracts", self.contract_ids),
            ("Products", f"{self.base_url}/api/data-products", self.product_ids),
        ]

        for entity_type, endpoint, created_ids in checks:
            try:
                # Extract path from full URL
                path = endpoint.replace(self.base_url, '')
                response = self._make_request('GET', path)
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else data.get('total', 0)
                    print(f"\n{entity_type}:")
                    print(f"  Created: {len(created_ids)}")
                    print(f"  Total in system: {count}")
                else:
                    print(f"\n{entity_type}: ✗ Could not verify ({response.status_code})")
            except Exception as e:
                print(f"\n{entity_type}: ✗ Error: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup Ontos demo data via REST API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local backend (default)
  python demo/setup_ontos_demo.py

  # Databricks App with identity token
  python demo/setup_ontos_demo.py \
    --base-url https://marcin-ontos-1444828305810485.aws.databricksapps.com \
    --databricks-profile e2-demo-field-eng

  # Custom local backend port
  python demo/setup_ontos_demo.py --base-url http://localhost:3000
        """
    )

    parser.add_argument(
        '--base-url',
        default='http://localhost:8000',
        help='Backend base URL (default: http://localhost:8000)'
    )

    parser.add_argument(
        '--databricks-profile',
        help='Databricks CLI profile name for authentication (for Databricks Apps)'
    )

    parser.add_argument(
        '--data-dir',
        default='src/backend/src/data',
        help='Directory containing demo data YAML files'
    )

    parser.add_argument(
        '--contracts-dir',
        default='contracts',
        help='Directory containing contract YAML files'
    )

    parser.add_argument(
        '--skip-domains',
        action='store_true',
        help='Skip domain creation'
    )

    parser.add_argument(
        '--skip-teams',
        action='store_true',
        help='Skip team creation'
    )

    parser.add_argument(
        '--skip-projects',
        action='store_true',
        help='Skip project creation'
    )

    parser.add_argument(
        '--skip-contracts',
        action='store_true',
        help='Skip contract creation'
    )

    parser.add_argument(
        '--skip-products',
        action='store_true',
        help='Skip product creation'
    )

    parser.add_argument(
        '--no-fail-fast',
        action='store_true',
        help='Continue on errors instead of stopping'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Ontos Healthcare Payor Demo Setup")
    print("=" * 80)
    print(f"\nBackend URL: {args.base_url}")
    print(f"Databricks Profile: {args.databricks_profile or 'None (local mode)'}")
    print(f"Data directory: {args.data_dir}")
    print(f"Contracts directory: {args.contracts_dir}")
    print(f"Fail fast: {not args.no_fail_fast}")

    # Initialize setup client
    setup = OntosSetup(
        args.base_url,
        databricks_profile=args.databricks_profile,
        fail_fast=not args.no_fail_fast
    )

    # Check backend health first
    if not setup.check_health():
        print("\n❌ Cannot reach backend. Please check:")
        if args.databricks_profile:
            print("   1. Is the Databricks App URL correct?")
            print("   2. Is the profile configured?")
            print(f"      databricks auth login --profile {args.databricks_profile}")
            print("   3. Try manually: databricks auth token --profile " + args.databricks_profile)
        else:
            print("   1. Is the backend running locally?")
            print("   2. Start with: cd src/backend && hatch -e dev run uvicorn src.app:app --reload --port 8000")
            print("   3. Is the URL correct?")
        print(f"\n   Tried: {args.base_url}")
        sys.exit(1)

    # Define demo configuration
    demo_config = {
        'domains': [
            {
                'name': 'Healthcare Core',
                'description': 'Foundational healthcare concepts applicable across all business functions',
                'tags': ['healthcare', 'enterprise', 'core']
            },
            {
                'name': 'Clinical',
                'description': 'Clinical data including diagnoses, procedures, medications, and care events',
                'parent_domain': 'Healthcare Core',
                'tags': ['clinical', 'hipaa', 'phi']
            },
            {
                'name': 'Claims & Operations',
                'description': 'Claims processing, provider networks, and operational data',
                'parent_domain': 'Healthcare Core',
                'tags': ['claims', 'operations', 'financial']
            },
            {
                'name': 'Member & Analytics',
                'description': 'Member profiles, engagement data, and analytical insights',
                'parent_domain': 'Healthcare Core',
                'tags': ['member', 'analytics', 'engagement']
            }
        ],
        'teams': [
            {
                'name': 'claims-engineering',
                'title': 'Claims Data Engineering Team',
                'domain_name': 'Claims & Operations',
                'description': 'Responsible for claims data pipelines, EDI processing, and provider data integration',
                'tags': ['claims', 'engineering', 'etl']
            },
            {
                'name': 'member-analytics',
                'title': 'Member Analytics Team',
                'domain_name': 'Member & Analytics',
                'description': 'Member experience analytics, segmentation, and engagement analysis',
                'tags': ['analytics', 'member', 'reporting']
            },
            {
                'name': 'clinical-data-science',
                'title': 'Clinical Data Science Team',
                'domain_name': 'Clinical',
                'description': 'Predictive modeling for care management, risk adjustment, and utilization forecasting',
                'tags': ['data-science', 'ml', 'clinical', 'predictive']
            },
            {
                'name': 'governance-compliance',
                'title': 'Data Governance & Compliance Team',
                'domain_name': 'Healthcare Core',
                'description': 'HIPAA compliance, data quality, and governance oversight',
                'tags': ['governance', 'compliance', 'hipaa', 'quality']
            }
        ],
        'projects': [
            {
                'name': 'claims-modernization',
                'title': 'Claims Processing Modernization',
                'type': 'TEAM',
                'owner_team': 'claims-engineering',
                'description': 'Modernize claims processing pipeline from EDI 837/835 to real-time adjudication',
                'tags': ['claims', 'modernization', 'automation']
            },
            {
                'name': 'member-360',
                'title': 'Member 360 Platform',
                'type': 'TEAM',
                'owner_team': 'member-analytics',
                'description': 'Unified member data platform integrating claims, clinical, and engagement data',
                'tags': ['member', 'platform', '360-view']
            },
            {
                'name': 'predictive-care-mgmt',
                'title': 'Predictive Care Management',
                'type': 'TEAM',
                'owner_team': 'clinical-data-science',
                'description': 'ML models for identifying high-risk members and reducing hospital readmissions',
                'tags': ['ml', 'predictive', 'care-management', 'risk']
            }
        ]
    }

    try:
        # Create entities in order
        if not args.skip_domains:
            setup.create_domains(demo_config['domains'])

        if not args.skip_teams:
            setup.create_teams(demo_config['teams'])

        if not args.skip_projects:
            setup.create_projects(demo_config['projects'])

        if not args.skip_contracts:
            setup.create_contracts(args.contracts_dir)

        if not args.skip_products:
            products_file = f"{args.data_dir}/data_products.yaml"
            setup.create_products(products_file)

        # Verify setup
        setup.verify_setup()

        print("\n" + "=" * 80)
        if setup.error_count > 0:
            print(f"⚠️  Demo Setup Completed with {setup.error_count} errors")
            print("=" * 80)
            sys.exit(1)
        else:
            print("✓ Demo Setup Complete!")
            print("=" * 80)
        print("\nNext steps:")
        print("1. Log into Ontos UI")
        print("2. Navigate to Settings → Data Domains to verify")
        print("3. Check Data Contracts and Data Products")
        print("4. Run data quality checks")

    except KeyboardInterrupt:
        print("\n\n⚠ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
