import random
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker

from apps.accounts.models import Profile
from apps.clients.models import Client, ClientContact
from apps.vessels.models import Vessel, VesselSpec, VesselPart
from apps.materials.models import (
    MaterialCategory,
    Material,
    StockMovement,
    MaterialRequest,
)
from apps.progress.models import Milestone, Task, WorkLog
from apps.documents.models import Document, Certification
from apps.maintenance.models import (
    MaintenanceType,
    MaintenanceSchedule,
    MaintenancePart,
    ServiceHistory,
)

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed NautiCore with realistic dummy data"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding NautiCore..."))
        users = self.create_users()
        clients = self.create_clients()
        vessels = self.create_vessels(clients, users)
        self.create_materials(users, vessels)
        self.create_progress(vessels, users)
        self.create_certifications(vessels)
        self.create_maintenance(vessels, users)
        self.stdout.write(self.style.SUCCESS("NautiCore seeded successfully!"))

    # ─── Users ───────────────────────────────────────────────────────────────

    def create_users(self):
        self.stdout.write("  Creating users...")
        users_data = [
            {
                "username": "admin_john",
                "first_name": "John",
                "last_name": "Smith",
                "role": "admin",
                "email": "john.smith@nauticore.com",
            },
            {
                "username": "mgr_sarah",
                "first_name": "Sarah",
                "last_name": "Johnson",
                "role": "manager",
                "email": "sarah.johnson@nauticore.com",
            },
            {
                "username": "mgr_david",
                "first_name": "David",
                "last_name": "Lee",
                "role": "manager",
                "email": "david.lee@nauticore.com",
            },
            {
                "username": "eng_ali",
                "first_name": "Ali",
                "last_name": "Hassan",
                "role": "engineer",
                "email": "ali.hassan@nauticore.com",
            },
            {
                "username": "eng_maria",
                "first_name": "Maria",
                "last_name": "Santos",
                "role": "engineer",
                "email": "maria.santos@nauticore.com",
            },
            {
                "username": "eng_raj",
                "first_name": "Raj",
                "last_name": "Kumar",
                "role": "engineer",
                "email": "raj.kumar@nauticore.com",
            },
            {
                "username": "proc_kevin",
                "first_name": "Kevin",
                "last_name": "Wong",
                "role": "procurement",
                "email": "kevin.wong@nauticore.com",
            },
            {
                "username": "viewer_tom",
                "first_name": "Tom",
                "last_name": "Brown",
                "role": "viewer",
                "email": "tom.brown@nauticore.com",
            },
        ]
        users = []
        for u in users_data:
            if not User.objects.filter(username=u["username"]).exists():
                user = User.objects.create_user(
                    username=u["username"],
                    email=u["email"],
                    password="NautiCore@2026",
                    first_name=u["first_name"],
                    last_name=u["last_name"],
                    role=u["role"],
                )
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        "phone": fake.phone_number()[:15],
                        "department": u["role"].title(),
                        "employee_id": f"NC-{random.randint(1000,9999)}",
                        "bio": fake.sentence(),
                    },
                )
                self.stdout.write(f'    Created user: {u["username"]} ({u["role"]})')
            users.append(User.objects.get(username=u["username"]))
        return users

    # ─── Clients ─────────────────────────────────────────────────────────────

    def create_clients(self):
        self.stdout.write("  Creating clients...")
        clients_data = [
            {
                "name": "Pacific Shipping Corp",
                "code": "PSC",
                "industry": "shipping",
                "country": "Singapore",
                "city": "Singapore",
            },
            {
                "name": "Indo Ocean Lines",
                "code": "IOL",
                "industry": "shipping",
                "country": "Indonesia",
                "city": "Jakarta",
            },
            {
                "name": "Borneo Petroleum Ltd",
                "code": "BPL",
                "industry": "oil_gas",
                "country": "Malaysia",
                "city": "Kuala Lumpur",
            },
            {
                "name": "Royal Navy Maritime",
                "code": "RNM",
                "industry": "military",
                "country": "Indonesia",
                "city": "Surabaya",
            },
            {
                "name": "Blue Horizon Ferries",
                "code": "BHF",
                "industry": "tourism",
                "country": "Indonesia",
                "city": "Bali",
            },
            {
                "name": "Nusantara Fishing Co",
                "code": "NFC",
                "industry": "fishing",
                "country": "Indonesia",
                "city": "Makassar",
            },
            {
                "name": "Asia Pacific Cargo",
                "code": "APC",
                "industry": "shipping",
                "country": "Philippines",
                "city": "Manila",
            },
            {
                "name": "Straits Government Port",
                "code": "SGP",
                "industry": "government",
                "country": "Singapore",
                "city": "Singapore",
            },
        ]
        clients = []
        for c in clients_data:
            client, created = Client.objects.get_or_create(
                code=c["code"],
                defaults={
                    "name": c["name"],
                    "industry": c["industry"],
                    "country": c["country"],
                    "city": c["city"],
                    "email": f"info@{c['code'].lower()}.com",
                    "phone": fake.phone_number()[:20],
                    "website": f"https://www.{c['code'].lower()}.com",
                    "status": "active",
                    "notes": fake.sentence(),
                },
            )
            if created:
                for position, is_primary in [
                    ("Operations Director", True),
                    ("Project Manager", False),
                ]:
                    ClientContact.objects.create(
                        client=client,
                        name=fake.name(),
                        position=position,
                        email=fake.company_email(),
                        phone=fake.phone_number()[:20],
                        is_primary=is_primary,
                    )
                self.stdout.write(f'    Created client: {c["name"]}')
            clients.append(client)
        return clients

    # ─── Vessels ─────────────────────────────────────────────────────────────

    def create_vessels(self, clients, users):
        self.stdout.write("  Creating vessels...")
        managers = [u for u in users if u.role in ["manager", "admin"]]

        vessels_data = [
            {
                "project_number": "NC-2024-001",
                "name": "MV Pacific Star",
                "vessel_type": "new_build",
                "ship_type": "cargo",
                "status": "delivered",
                "client_idx": 0,
            },
            {
                "project_number": "NC-2024-002",
                "name": "MV Borneo Explorer",
                "vessel_type": "new_build",
                "ship_type": "tanker",
                "status": "completed",
                "client_idx": 2,
            },
            {
                "project_number": "NC-2025-001",
                "name": "KRI Nusantara",
                "vessel_type": "new_build",
                "ship_type": "patrol",
                "status": "testing",
                "client_idx": 3,
            },
            {
                "project_number": "NC-2025-002",
                "name": "MV Bali Dream",
                "vessel_type": "new_build",
                "ship_type": "ferry",
                "status": "in_progress",
                "client_idx": 4,
            },
            {
                "project_number": "NC-2025-003",
                "name": "TB Mighty Tug",
                "vessel_type": "new_build",
                "ship_type": "tugboat",
                "status": "in_progress",
                "client_idx": 1,
            },
            {
                "project_number": "NC-2025-004",
                "name": "MV Makassar Pride",
                "vessel_type": "repair",
                "ship_type": "fishing",
                "status": "in_progress",
                "client_idx": 5,
            },
            {
                "project_number": "NC-2025-005",
                "name": "MV Manila Express",
                "vessel_type": "new_build",
                "ship_type": "cargo",
                "status": "planning",
                "client_idx": 6,
            },
            {
                "project_number": "NC-2026-001",
                "name": "MV Singapore Pride",
                "vessel_type": "maintenance",
                "ship_type": "cargo",
                "status": "planning",
                "client_idx": 7,
            },
            {
                "project_number": "NC-2026-002",
                "name": "BG Pacific Barge",
                "vessel_type": "new_build",
                "ship_type": "barge",
                "status": "planning",
                "client_idx": 0,
            },
            {
                "project_number": "NC-2026-003",
                "name": "TB Indo Force",
                "vessel_type": "new_build",
                "ship_type": "tugboat",
                "status": "planning",
                "client_idx": 1,
            },
        ]

        specs_data = [
            {
                "length": 185.5,
                "beam": 28.0,
                "draft": 10.5,
                "gross_ton": 18500,
                "horsepower": 12000,
                "speed": 14.5,
            },
            {
                "length": 220.0,
                "beam": 32.0,
                "draft": 12.0,
                "gross_ton": 35000,
                "horsepower": 15000,
                "speed": 13.0,
            },
            {
                "length": 62.0,
                "beam": 9.5,
                "draft": 3.2,
                "gross_ton": 450,
                "horsepower": 4500,
                "speed": 28.0,
            },
            {
                "length": 95.0,
                "beam": 18.0,
                "draft": 4.5,
                "gross_ton": 2800,
                "horsepower": 6000,
                "speed": 18.0,
            },
            {
                "length": 38.0,
                "beam": 11.0,
                "draft": 4.8,
                "gross_ton": 380,
                "horsepower": 5600,
                "speed": 12.0,
            },
            {
                "length": 42.0,
                "beam": 8.5,
                "draft": 3.8,
                "gross_ton": 320,
                "horsepower": 1800,
                "speed": 10.0,
            },
            {
                "length": 165.0,
                "beam": 26.0,
                "draft": 9.5,
                "gross_ton": 14000,
                "horsepower": 10000,
                "speed": 15.0,
            },
            {
                "length": 175.0,
                "beam": 27.5,
                "draft": 10.0,
                "gross_ton": 16000,
                "horsepower": 11000,
                "speed": 14.0,
            },
            {
                "length": 75.0,
                "beam": 22.0,
                "draft": 3.0,
                "gross_ton": 1800,
                "horsepower": 2400,
                "speed": 8.0,
            },
            {
                "length": 32.0,
                "beam": 10.0,
                "draft": 4.2,
                "gross_ton": 280,
                "horsepower": 4800,
                "speed": 11.0,
            },
        ]

        vessels = []
        today = date.today()

        for i, v in enumerate(vessels_data):
            if Vessel.objects.filter(project_number=v["project_number"]).exists():
                vessels.append(Vessel.objects.get(project_number=v["project_number"]))
                continue

            start = today - timedelta(days=random.randint(180, 730))
            target = start + timedelta(days=random.randint(180, 540))

            vessel = Vessel.objects.create(
                project_number=v["project_number"],
                name=v["name"],
                client=clients[v["client_idx"]],
                project_manager=random.choice(managers),
                vessel_type=v["vessel_type"],
                ship_type=v["ship_type"],
                status=v["status"],
                start_date=start,
                target_date=target,
                completed_date=(
                    today - timedelta(days=30)
                    if v["status"] in ["completed", "delivered"]
                    else None
                ),
                description=f"Construction of {v['name']} for {clients[v['client_idx']].name}",
                notes=fake.sentence(),
            )

            spec = specs_data[i]
            VesselSpec.objects.create(
                vessel=vessel,
                length=Decimal(str(spec["length"])),
                beam=Decimal(str(spec["beam"])),
                draft=Decimal(str(spec["draft"])),
                gross_ton=Decimal(str(spec["gross_ton"])),
                horsepower=spec["horsepower"],
                speed=Decimal(str(spec["speed"])),
                material="Steel",
                engine_type=random.choice(
                    ["MAN B&W", "Caterpillar", "Wärtsilä", "Cummins"]
                ),
                class_notation=random.choice(
                    ["BKI", "DNV GL", "Bureau Veritas", "Lloyd Register"]
                ),
            )

            parts = [
                ("Main Engine", "ENG-001", 1),
                ("Propeller Shaft", "PROP-001", 1),
                ("Anchor System", "ANC-001", 1),
                ("Navigation Radar", "NAV-001", 1),
                ("Life Raft", "SAF-001", random.randint(4, 8)),
                ("Generator Set", "GEN-001", random.randint(2, 3)),
                ("Steering Gear", "STG-001", 1),
            ]
            for name, part_num, qty in parts:
                VesselPart.objects.create(
                    vessel=vessel,
                    name=name,
                    part_number=f"{part_num}-{vessel.project_number}",
                    quantity=qty,
                    unit="pcs",
                    status=random.choice(
                        ["pending", "ordered", "received", "installed"]
                    ),
                    supplier=fake.company(),
                )

            self.stdout.write(f'    Created vessel: {v["name"]} ({v["status"]})')
            vessels.append(vessel)
        return vessels

    # ─── Materials ───────────────────────────────────────────────────────────

    def create_materials(self, users, vessels):
        self.stdout.write("  Creating materials...")
        procurement_users = [u for u in users if u.role in ["procurement", "admin"]]
        today = date.today()

        categories_data = [
            (
                "Steel & Metal",
                "#6c757d",
                [
                    "Steel Plate 10mm",
                    "Steel Plate 20mm",
                    "Steel Bar 50mm",
                    "Aluminum Sheet",
                ],
            ),
            (
                "Engine & Machinery",
                "#dc3545",
                ["Engine Oil SAE 40", "Hydraulic Oil", "Coolant Fluid", "Gear Oil"],
            ),
            (
                "Electrical",
                "#ffc107",
                [
                    "Marine Cable 4mm",
                    "Marine Cable 6mm",
                    "LED Light 24V",
                    "Circuit Breaker",
                ],
            ),
            (
                "Paint & Coating",
                "#0d6efd",
                [
                    "Anti-Corrosion Primer",
                    "Anti-Fouling Paint",
                    "Deck Paint",
                    "Epoxy Coating",
                ],
            ),
            (
                "Safety Equipment",
                "#198754",
                [
                    "Life Jacket Adult",
                    "Fire Extinguisher",
                    "Safety Helmet",
                    "First Aid Kit",
                ],
            ),
            (
                "Fasteners & Fittings",
                "#6610f2",
                ["Bolt M16x50", "Nut M16", "Washer M16", "Weld Rod 3.2mm"],
            ),
        ]

        all_materials = []
        for cat_name, color, items in categories_data:
            category, _ = MaterialCategory.objects.get_or_create(
                name=cat_name,
                defaults={
                    "description": f"{cat_name} for shipbuilding",
                    "color": color,
                },
            )
            for item_name in items:
                code = f"{cat_name[:3].upper()}-{item_name[:4].upper()}-{random.randint(100,999)}".replace(
                    " ", "-"
                ).replace(
                    "&", "N"
                )
                material, created = Material.objects.get_or_create(
                    name=item_name,
                    defaults={
                        "code": code,
                        "category": category,
                        "description": f"{item_name} for marine construction",
                        "unit": random.choice(["pcs", "kg", "meter", "liter", "sheet"]),
                        "current_stock": Decimal(str(random.randint(50, 500))),
                        "minimum_stock": Decimal(str(random.randint(10, 50))),
                        "unit_price": Decimal(str(random.randint(10, 5000))),
                        "supplier": fake.company(),
                        "location": f"Warehouse {random.choice(['A','B','C'])}, Rack {random.randint(1,20)}",
                    },
                )
                if created:
                    StockMovement.objects.create(
                        material=material,
                        movement_type="in",
                        quantity=material.current_stock,
                        unit_price=material.unit_price,
                        reference=f"PO-INIT-{random.randint(1000,9999)}",
                        notes="Initial stock",
                        performed_by=random.choice(procurement_users),
                        movement_date=today - timedelta(days=random.randint(30, 180)),
                    )
                    all_materials.append(material)

        self.stdout.write(f"    Created {len(all_materials)} materials")

        engineers = [u for u in users if u.role in ["engineer", "manager"]]
        in_progress = [v for v in vessels if v.status == "in_progress"]
        for vessel in in_progress[:3]:
            for material in random.sample(
                list(Material.objects.all()), min(5, Material.objects.count())
            ):
                MaterialRequest.objects.get_or_create(
                    vessel=vessel,
                    material=material,
                    defaults={
                        "requested_by": random.choice(engineers),
                        "quantity_needed": Decimal(str(random.randint(5, 50))),
                        "status": random.choice(["pending", "approved", "fulfilled"]),
                        "needed_by": today + timedelta(days=random.randint(7, 60)),
                        "notes": f"Required for {vessel.name}",
                    },
                )

    # ─── Progress ────────────────────────────────────────────────────────────

    def create_progress(self, vessels, users):
        self.stdout.write("  Creating milestones and tasks...")
        engineers = [u for u in users if u.role in ["engineer", "manager"]]
        today = date.today()

        milestones_template = [
            (
                "Design & Engineering",
                0,
                [
                    "Prepare technical drawings",
                    "Engineering review",
                    "Class approval",
                    "Final design sign-off",
                ],
            ),
            (
                "Steel Cutting & Forming",
                1,
                ["Steel plate cutting", "Frame forming", "Quality inspection"],
            ),
            (
                "Hull Construction",
                2,
                ["Keel laying", "Frame erection", "Shell plating", "Hull welding"],
            ),
            (
                "Superstructure",
                3,
                ["Deck installation", "Accommodation block", "Bridge construction"],
            ),
            (
                "Machinery Installation",
                4,
                ["Main engine installation", "Generator installation", "Piping system"],
            ),
            (
                "Electrical & Navigation",
                5,
                ["Main switchboard", "Navigation equipment", "Communication system"],
            ),
            (
                "Outfitting & Interior",
                6,
                ["Accommodation fitting", "Safety equipment", "Paint & coating"],
            ),
            (
                "Sea Trial & Delivery",
                7,
                ["Dock trial", "Sea trial", "Class survey", "Delivery preparation"],
            ),
        ]

        status_map = {
            "planning": (0, "not_started"),
            "in_progress": (40, "in_progress"),
            "testing": (85, "in_progress"),
            "completed": (100, "completed"),
            "delivered": (100, "completed"),
        }

        for vessel in vessels:
            if vessel.milestones.exists():
                continue

            base_pct, _ = status_map.get(vessel.status, (0, "not_started"))

            for ms_name, order, task_names in milestones_template:
                if vessel.status == "planning" and order > 0:
                    ms_pct, ms_status = 0, "not_started"
                elif vessel.status in ["completed", "delivered"]:
                    ms_pct, ms_status = 100, "completed"
                else:
                    progress = max(0, base_pct - (order * 12))
                    ms_pct = min(100, progress)
                    ms_status = (
                        "completed"
                        if ms_pct >= 100
                        else ("in_progress" if ms_pct > 0 else "not_started")
                    )

                milestone = Milestone.objects.create(
                    vessel=vessel,
                    name=ms_name,
                    description=f"{ms_name} phase for {vessel.name}",
                    status=ms_status,
                    order=order,
                    completion_pct=Decimal(str(ms_pct)),
                    assigned_to=random.choice(engineers),
                    start_date=vessel.start_date,
                    target_date=(
                        vessel.start_date + timedelta(days=(order + 1) * 60)
                        if vessel.start_date
                        else None
                    ),
                    completed_date=(
                        today - timedelta(days=random.randint(1, 90))
                        if ms_status == "completed"
                        else None
                    ),
                )

                for task_name in task_names:
                    if ms_status == "completed":
                        t_pct, t_status = 100, "completed"
                    elif ms_status == "not_started":
                        t_pct, t_status = 0, "todo"
                    else:
                        t_pct = random.randint(0, 100)
                        t_status = (
                            "completed"
                            if t_pct >= 100
                            else ("in_progress" if t_pct > 0 else "todo")
                        )

                    task = Task.objects.create(
                        milestone=milestone,
                        name=task_name,
                        description=f"{task_name} for {vessel.name}",
                        status=t_status,
                        priority=random.choice(["low", "medium", "high"]),
                        completion_pct=Decimal(str(t_pct)),
                        assigned_to=random.choice(engineers),
                        start_date=milestone.start_date,
                        due_date=milestone.target_date,
                        completed_date=(
                            today - timedelta(days=random.randint(1, 60))
                            if t_status == "completed"
                            else None
                        ),
                    )

                    if vessel.status == "in_progress":
                        for _ in range(random.randint(2, 5)):
                            WorkLog.objects.create(
                                vessel=vessel,
                                task=task,
                                logged_by=random.choice(engineers),
                                date=today - timedelta(days=random.randint(0, 60)),
                                hours=Decimal(str(round(random.uniform(4, 10), 1))),
                                description=f"{fake.sentence()} Work on {ms_name}.",
                                issues=fake.sentence() if random.random() > 0.7 else "",
                            )

        self.stdout.write(f"    Created milestones for {len(vessels)} vessels")

    # ─── Certifications ──────────────────────────────────────────────────────

    def create_certifications(self, vessels):
        self.stdout.write("  Creating certifications...")
        today = date.today()

        cert_types = [
            ("class", "Bureau Veritas Class Certificate"),
            ("safety", "Safety Equipment Certificate"),
            ("tonnage", "International Tonnage Certificate"),
            ("load_line", "International Load Line Certificate"),
            ("marpol", "MARPOL Prevention Certificate"),
            ("radio", "Radio Station License"),
        ]

        active_vessels = [
            v for v in vessels if v.status in ["delivered", "completed", "testing"]
        ]
        for vessel in active_vessels:
            if vessel.certifications.exists():
                continue
            for cert_type, cert_name in cert_types:
                issued = today - timedelta(days=random.randint(30, 365))
                expiry = issued + timedelta(days=random.randint(365, 1825))
                days_left = (expiry - today).days
                status = (
                    "expired"
                    if days_left < 0
                    else ("expiring_soon" if days_left <= 30 else "valid")
                )
                Certification.objects.create(
                    vessel=vessel,
                    cert_type=cert_type,
                    title=f"{cert_name} — {vessel.name}",
                    cert_number=f"CERT-{vessel.project_number[-3:]}-{random.randint(10000,99999)}",
                    issuing_body=random.choice(
                        ["BKI", "Bureau Veritas", "DNV GL", "Lloyd Register"]
                    ),
                    issued_date=issued,
                    expiry_date=expiry,
                    status=status,
                    notes=f"Issued for {vessel.name}",
                )

        self.stdout.write(
            f"    Created certifications for {len(active_vessels)} vessels"
        )

    # ─── Maintenance ─────────────────────────────────────────────────────────

    def create_maintenance(self, vessels, users):
        self.stdout.write("  Creating maintenance data...")
        engineers = [u for u in users if u.role in ["engineer", "manager", "admin"]]
        today = date.today()

        types_data = [
            ("Main Engine Service", 90, "Full service of main engine"),
            ("Hull Inspection", 180, "Visual and structural hull inspection"),
            ("Navigation Equipment Check", 30, "Calibration of navigation instruments"),
            ("Safety Equipment Inspection", 30, "Inspection of safety systems"),
            ("Electrical System Check", 60, "Inspection of electrical systems"),
            (
                "Propeller & Shaft Service",
                365,
                "Service of propeller shaft and bearings",
            ),
            ("Anchor & Mooring Check", 90, "Inspection of anchor and mooring systems"),
            ("Bilge System Service", 60, "Cleaning and testing of bilge pumps"),
            ("Generator Service", 120, "Full service of generator sets"),
            ("Steering Gear Service", 90, "Inspection of steering gear system"),
        ]

        maintenance_types = []
        for name, interval, desc in types_data:
            mt, _ = MaintenanceType.objects.get_or_create(
                name=name, defaults={"interval_days": interval, "description": desc}
            )
            maintenance_types.append(mt)

        priorities = ["low", "medium", "high", "critical"]

        for vessel in vessels:
            if vessel.maintenance_schedules.exists():
                continue

            selected_types = random.sample(
                maintenance_types, min(5, len(maintenance_types))
            )
            for i, mt in enumerate(selected_types):
                if i % 3 == 0:
                    sched_date = today - timedelta(days=random.randint(30, 120))
                    comp_date = sched_date + timedelta(days=random.randint(1, 5))
                    status = "completed"
                    next_due = sched_date + timedelta(days=mt.interval_days)
                elif i % 3 == 1:
                    sched_date = today + timedelta(days=random.randint(7, 60))
                    comp_date = None
                    status = "scheduled"
                    next_due = None
                else:
                    sched_date = today - timedelta(days=random.randint(5, 30))
                    comp_date = None
                    status = "scheduled"
                    next_due = None

                schedule = MaintenanceSchedule.objects.create(
                    vessel=vessel,
                    maintenance_type=mt,
                    title=f"{mt.name} — {vessel.name}",
                    description=mt.description,
                    status=status,
                    priority=random.choice(priorities),
                    scheduled_date=sched_date,
                    completed_date=comp_date,
                    next_due_date=next_due,
                    assigned_to=random.choice(engineers),
                    estimated_hours=Decimal(str(random.randint(4, 24))),
                    actual_hours=(
                        Decimal(str(random.randint(4, 24)))
                        if status == "completed"
                        else None
                    ),
                    notes=fake.sentence(),
                    findings=fake.sentence() if status == "completed" else "",
                )

                materials = list(Material.objects.all())
                if materials and status == "completed":
                    for material in random.sample(materials, min(3, len(materials))):
                        MaintenancePart.objects.get_or_create(
                            maintenance=schedule,
                            material=material,
                            defaults={
                                "quantity": Decimal(str(random.randint(1, 10))),
                                "notes": f"Used during {mt.name}",
                            },
                        )
                    ServiceHistory.objects.get_or_create(
                        vessel=vessel,
                        maintenance=schedule,
                        defaults={
                            "title": f"Completed: {mt.name}",
                            "description": schedule.description,
                            "service_date": comp_date,
                            "performed_by": random.choice(engineers),
                            "hours_spent": schedule.actual_hours or 0,
                            "findings": schedule.findings,
                            "next_service_date": next_due,
                        },
                    )

        self.stdout.write(f"    Created maintenance for {len(vessels)} vessels")
