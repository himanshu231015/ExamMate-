"""Seed data with authentic RGPV academic context, syllabus, PYQs, and test accounts."""

from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.academic import (
    University,
    Degree,
    Branch,
    AcademicScheme,
    Subject,
    SyllabusDocument,
    SyllabusUnit,
    SyllabusTopic,
    VerificationStatus,
)
from app.models.question_paper import (
    QuestionPaper,
    ExtractedQuestion,
    ExamType,
    ExamSession,
)


def seed_database(db: Session):
    """Seed initial users, university hierarchy, syllabus, and PYQ records."""

    # 1. Seed Users (if not exists)
    if not db.query(User).filter(User.email == "admin@rgpvexammate.edu").first():
        admin = User(
            email="admin@rgpvexammate.edu",
            hashed_password=hash_password("Admin@123"),
            full_name="RGPV Administrator",
            role=UserRole.ADMIN,
            is_active=True,
        )
        reviewer = User(
            email="reviewer@rgpvexammate.edu",
            hashed_password=hash_password("Reviewer@123"),
            full_name="Prof. Sharma (Authorized Reviewer)",
            role=UserRole.REVIEWER,
            is_active=True,
        )
        contributor = User(
            email="contributor@rgpvexammate.edu",
            hashed_password=hash_password("Contrib@123"),
            full_name="Aman Verma (Student Contributor)",
            role=UserRole.CONTRIBUTOR,
            is_active=True,
        )
        student = User(
            email="student@rgpvexammate.edu",
            hashed_password=hash_password("Student@123"),
            full_name="Priya Patel (B.Tech AIML Student)",
            role=UserRole.STUDENT,
            is_active=True,
        )
        db.add_all([admin, reviewer, contributor, student])
        db.commit()

    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()

    # 2. Seed University
    rgpv = db.query(University).filter(University.short_name == "RGPV").first()
    if not rgpv:
        rgpv = University(
            name="Rajiv Gandhi Proudyogiki Vishwavidyalaya",
            short_name="RGPV",
            state="Madhya Pradesh",
            city="Bhopal",
            website="https://www.rgpv.ac.in",
        )
        db.add(rgpv)
        db.commit()
        db.refresh(rgpv)

    # 3. Seed Degree
    btech = db.query(Degree).filter(Degree.code == "B.Tech", Degree.university_id == rgpv.id).first()
    if not btech:
        btech = Degree(
            university_id=rgpv.id,
            name="Bachelor of Technology",
            code="B.Tech",
            duration_years=4,
        )
        db.add(btech)
        db.commit()
        db.refresh(btech)

    # 4. Seed Branches
    cse = db.query(Branch).filter(Branch.code == "CSE", Branch.degree_id == btech.id).first()
    if not cse:
        cse = Branch(
            degree_id=btech.id,
            name="Computer Science & Engineering",
            code="CSE",
        )
        db.add(cse)

    aiml = db.query(Branch).filter(Branch.code == "AIML", Branch.degree_id == btech.id).first()
    if not aiml:
        aiml = Branch(
            degree_id=btech.id,
            name="Computer Science & Engineering (AI & ML)",
            code="AIML",
        )
        db.add(aiml)

    db.commit()
    db.refresh(cse)
    db.refresh(aiml)

    # 5. Seed Schemes
    cbgs = db.query(AcademicScheme).filter(AcademicScheme.code == "CBGS", AcademicScheme.university_id == rgpv.id).first()
    if not cbgs:
        cbgs = AcademicScheme(
            university_id=rgpv.id,
            name="Choice Based Grading System (CBGS-2019)",
            code="CBGS",
            start_year=2019,
            description="Official RGPV grading system curriculum introduced in 2019.",
        )
        db.add(cbgs)
        db.commit()
        db.refresh(cbgs)

    # 6. Seed Subjects
    # Subject 1: Data Structures (CS-301)
    ds = db.query(Subject).filter(Subject.code == "CS-301", Subject.scheme_id == cbgs.id).first()
    if not ds:
        ds = Subject(
            branch_id=cse.id,
            scheme_id=cbgs.id,
            name="Data Structures",
            code="CS-301",
            semester_number=3,
            credits=4,
            description="Fundamental data structures: Stacks, Queues, Linked Lists, Trees, Graphs, Sorting & Hashing.",
        )
        db.add(ds)
        db.commit()
        db.refresh(ds)

        # Syllabus Document for CS-301
        doc_ds = SyllabusDocument(
            subject_id=ds.id,
            academic_year="2023-2024",
            source_url="https://www.rgpv.ac.in/Uni/Frm_ViewScheme.aspx",
            verification_status=VerificationStatus.VERIFIED,
            raw_text="RGPV B.Tech III Semester CS-301 Data Structures Syllabus: Unit I Stacks & Queues, Unit II Linked Lists, Unit III Trees & BST, Unit IV Graphs & Spanning Trees, Unit V Sorting & Hashing.",
            uploaded_by_id=admin_user.id if admin_user else None,
        )
        db.add(doc_ds)

        # Units & Topics for CS-301
        # Unit 1
        u1 = SyllabusUnit(
            subject_id=ds.id,
            unit_number=1,
            title="Unit I: Introduction to Data Structures, Stacks and Queues",
            description="Linear data structures, Array representation, Stack ADT, Infix to Postfix conversion, Circular Queues, Deque and Priority Queues.",
        )
        db.add(u1)
        db.flush()

        t1_1 = SyllabusTopic(
            unit_id=u1.id,
            topic_name="Stack ADT and Applications",
            subtopics="Push, Pop, Peek operations, Expression Evaluation, Infix to Postfix conversion using Stacks.",
            learning_objectives="Understand LIFO principle and algorithm for infix-to-postfix conversion.",
            importance_level="high",
        )
        t1_2 = SyllabusTopic(
            unit_id=u1.id,
            topic_name="Circular Queue and Priority Queue",
            subtopics="Queue overflow/underflow, Circular queue array implementation, Priority queue heap representation.",
            learning_objectives="Differentiate linear queue drawbacks and implement circular queue logic.",
            importance_level="high",
        )
        db.add_all([t1_1, t1_2])

        # Unit 2
        u2 = SyllabusUnit(
            subject_id=ds.id,
            unit_number=2,
            title="Unit II: Linked Lists and Dynamic Memory",
            description="Singly linked lists, Doubly linked lists, Circular linked lists, Applications such as Polynomial representation and addition.",
        )
        db.add(u2)
        db.flush()

        t2_1 = SyllabusTopic(
            unit_id=u2.id,
            topic_name="Singly and Doubly Linked Lists",
            subtopics="Node structure, Insertion at beginning/end/middle, Deletion, Reversal of linked list.",
            learning_objectives="Implement dynamic data structures with pointer manipulation.",
            importance_level="high",
        )
        t2_2 = SyllabusTopic(
            unit_id=u2.id,
            topic_name="Polynomial Representation and Addition",
            subtopics="Linked representation of single and multi-variable polynomials, Addition algorithms.",
            learning_objectives="Apply linked lists to solve symbolic mathematical algebra problems.",
            importance_level="medium",
        )
        db.add_all([t2_1, t2_2])

        # Unit 3
        u3 = SyllabusUnit(
            subject_id=ds.id,
            unit_number=3,
            title="Unit III: Trees and Hierarchical Data Structures",
            description="Binary Trees, Tree Traversals, Binary Search Tree (BST), AVL Trees with Rotations, Threaded Binary Trees, Introduction to B-Trees.",
        )
        db.add(u3)
        db.flush()

        t3_1 = SyllabusTopic(
            unit_id=u3.id,
            topic_name="Binary Search Trees (BST)",
            subtopics="BST properties, Searching, Insertion, Deletion cases (leaf, single child, two children).",
            learning_objectives="Demonstrate BST construction and analyze average O(log n) performance.",
            importance_level="high",
        )
        t3_2 = SyllabusTopic(
            unit_id=u3.id,
            topic_name="AVL Trees and Rotations",
            subtopics="Balance Factor, LL, RR, LR, RL Rotations, Insertion and Rebalancing step-by-step.",
            learning_objectives="Solve AVL tree rotation numerical problems frequently asked in RGPV exams.",
            importance_level="high",
        )
        db.add_all([t3_1, t3_2])

        # Unit 4
        u4 = SyllabusUnit(
            subject_id=ds.id,
            unit_number=4,
            title="Unit IV: Graph Algorithms",
            description="Graph representations, BFS and DFS traversals, Minimum Spanning Trees (Prim's and Kruskal's algorithms), Shortest Path (Dijkstra's algorithm).",
        )
        db.add(u4)
        db.flush()

        t4_1 = SyllabusTopic(
            unit_id=u4.id,
            topic_name="Graph Traversals (BFS and DFS)",
            subtopics="Adjacency Matrix, Adjacency List, Breadth First Search using Queue, Depth First Search using Stack/Recursion.",
            learning_objectives="Execute traversal orders on given graphs.",
            importance_level="high",
        )
        t4_2 = SyllabusTopic(
            unit_id=u4.id,
            topic_name="Minimum Spanning Tree (MST)",
            subtopics="Kruskal's Algorithm using Disjoint Sets, Prim's Greedy Algorithm, Cut property.",
            learning_objectives="Step-by-step derivation of MST for weighted undirected graphs.",
            importance_level="high",
        )
        db.add_all([t4_1, t4_2])

        # Unit 5
        u5 = SyllabusUnit(
            subject_id=ds.id,
            unit_number=5,
            title="Unit V: Searching, Sorting and Hashing",
            description="Internal and external sorting, Quick Sort, Merge Sort, Heap Sort, Hashing techniques, Collision resolution methods.",
        )
        db.add(u5)
        db.flush()

        t5_1 = SyllabusTopic(
            unit_id=u5.id,
            topic_name="Quick Sort and Merge Sort Analysis",
            subtopics="Divide and conquer partitioning, Worst-case and average-case time complexities.",
            learning_objectives="Trace sorting steps and write recurrence relations.",
            importance_level="high",
        )
        t5_2 = SyllabusTopic(
            unit_id=u5.id,
            topic_name="Hashing and Collision Resolution",
            subtopics="Hash functions (Division, Mid-square, Multiplication), Linear Probing, Quadratic Probing, Chaining.",
            learning_objectives="Calculate load factors and resolve collision sequences.",
            importance_level="high",
        )
        db.add_all([t5_1, t5_2])
        db.commit()

        # 7. Seed Real Exam Question Papers & PYQs for CS-301
        # Paper 1: Dec 2023
        p_dec23 = QuestionPaper(
            subject_id=ds.id,
            scheme_id=cbgs.id,
            exam_year=2023,
            exam_session=ExamSession.DECEMBER,
            exam_type=ExamType.MAIN,
            source_url="https://www.rgpvonline.com/papers/btech-cs-3-sem-data-structures-cs-301-dec-2023.pdf",
            total_marks=70,
            verification_status=VerificationStatus.VERIFIED,
            approved_by_id=admin_user.id if admin_user else None,
        )
        db.add(p_dec23)
        db.flush()

        # Questions for Dec 2023
        q1 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u1.id,
            topic_id=t1_1.id,
            question_number=1,
            sub_question="a",
            question_text="What is a Stack ADT? Explain the algorithm to convert an infix expression into a postfix expression using stack with a suitable example: (A + B * C) / (D - E).",
            marks=7,
            page_number=1,
            confidence_score=0.98,
            is_human_verified=True,
        )
        q2 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u1.id,
            topic_id=t1_2.id,
            question_number=1,
            sub_question="b",
            question_text="Explain the circular queue with its insertion and deletion algorithms. Why is a circular queue preferred over a linear queue?",
            marks=7,
            page_number=1,
            confidence_score=0.97,
            is_human_verified=True,
        )
        q3 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u2.id,
            topic_id=t2_1.id,
            question_number=2,
            sub_question="a",
            question_text="Write a C/C++ function to reverse a singly linked list in-place without using extra auxiliary memory.",
            marks=7,
            page_number=1,
            confidence_score=0.99,
            is_human_verified=True,
        )
        q4 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u3.id,
            topic_id=t3_2.id,
            question_number=3,
            sub_question="a",
            question_text="Construct an AVL tree by inserting the following key elements sequentially: 21, 26, 30, 9, 4, 14, 28, 18, 15, 10. Show every rotation step clearly.",
            marks=14,
            page_number=2,
            confidence_score=0.99,
            is_human_verified=True,
        )
        q5 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u4.id,
            topic_id=t4_2.id,
            question_number=4,
            sub_question="a",
            question_text="Explain Prim's algorithm for finding the Minimum Spanning Tree of a weighted graph. Find the MST for the given 6-vertex weighted graph.",
            marks=7,
            page_number=2,
            confidence_score=0.96,
            is_human_verified=True,
        )
        q6 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u5.id,
            topic_id=t5_2.id,
            question_number=5,
            sub_question="a",
            question_text="What is collision in hashing? Discuss open addressing collision resolution techniques: Linear Probing and Quadratic Probing with formulas.",
            marks=7,
            page_number=2,
            confidence_score=0.98,
            is_human_verified=True,
        )
        q7 = ExtractedQuestion(
            paper_id=p_dec23.id,
            unit_id=u1.id,
            topic_id=t1_1.id,
            question_number=6,
            sub_question="a",
            question_text="State the time complexity of pushing and popping in a stack.",
            marks=2,
            page_number=1,
            confidence_score=1.0,
            is_human_verified=True,
        )

        db.add_all([q1, q2, q3, q4, q5, q6, q7])

        # Paper 2: June 2023
        p_jun23 = QuestionPaper(
            subject_id=ds.id,
            scheme_id=cbgs.id,
            exam_year=2023,
            exam_session=ExamSession.JUNE,
            exam_type=ExamType.MAIN,
            source_url="https://www.rgpvonline.com/papers/btech-cs-3-sem-data-structures-cs-301-june-2023.pdf",
            total_marks=70,
            verification_status=VerificationStatus.VERIFIED,
            approved_by_id=admin_user.id if admin_user else None,
        )
        db.add(p_jun23)
        db.flush()

        q2_1 = ExtractedQuestion(
            paper_id=p_jun23.id,
            unit_id=u3.id,
            topic_id=t3_1.id,
            question_number=1,
            sub_question="a",
            question_text="Define Binary Search Tree (BST). Explain how deletion of a node having two children is performed with an illustrative example.",
            marks=7,
            page_number=1,
            confidence_score=0.98,
            is_human_verified=True,
        )
        q2_2 = ExtractedQuestion(
            paper_id=p_jun23.id,
            unit_id=u5.id,
            topic_id=t5_1.id,
            question_number=2,
            sub_question="a",
            question_text="Trace Quick Sort algorithm on array [45, 12, 89, 34, 70, 23, 56]. Discuss its best, average, and worst-case time complexities.",
            marks=7,
            page_number=1,
            confidence_score=0.97,
            is_human_verified=True,
        )
        q2_3 = ExtractedQuestion(
            paper_id=p_jun23.id,
            unit_id=u4.id,
            topic_id=t4_1.id,
            question_number=3,
            sub_question="a",
            question_text="Compare Breadth First Search (BFS) and Depth First Search (DFS) traversals in terms of data structures used and time complexities.",
            marks=7,
            page_number=2,
            confidence_score=0.99,
            is_human_verified=True,
        )
        db.add_all([q2_1, q2_2, q2_3])

        # Paper 3: Dec 2022
        p_dec22 = QuestionPaper(
            subject_id=ds.id,
            scheme_id=cbgs.id,
            exam_year=2022,
            exam_session=ExamSession.DECEMBER,
            exam_type=ExamType.MAIN,
            source_url="https://www.rgpvonline.com/papers/btech-cs-3-sem-data-structures-cs-301-dec-2022.pdf",
            total_marks=70,
            verification_status=VerificationStatus.VERIFIED,
            approved_by_id=admin_user.id if admin_user else None,
        )
        db.add(p_dec22)
        db.flush()

        q3_1 = ExtractedQuestion(
            paper_id=p_dec22.id,
            unit_id=u3.id,
            topic_id=t3_2.id,
            question_number=1,
            sub_question="a",
            question_text="Explain AVL tree rotations (LL, RR, LR, RL) with balance factor definitions and diagrammatic representations.",
            marks=7,
            page_number=1,
            confidence_score=0.98,
            is_human_verified=True,
        )
        q3_2 = ExtractedQuestion(
            paper_id=p_dec22.id,
            unit_id=u4.id,
            topic_id=t4_2.id,
            question_number=2,
            sub_question="a",
            question_text="Explain Kruskal's algorithm to obtain Minimum Spanning Tree with an example. How does it detect cycles?",
            marks=7,
            page_number=2,
            confidence_score=0.97,
            is_human_verified=True,
        )
        db.add_all([q3_1, q3_2])

        db.commit()

    # Subject 2: Analysis & Design of Algorithms (CS-402)
    ada = db.query(Subject).filter(Subject.code == "CS-402", Subject.scheme_id == cbgs.id).first()
    if not ada:
        ada = Subject(
            branch_id=cse.id,
            scheme_id=cbgs.id,
            name="Analysis & Design of Algorithms",
            code="CS-402",
            semester_number=4,
            credits=4,
            description="Algorithm design paradigms: Divide & Conquer, Greedy, Dynamic Programming, Backtracking, NP-Completeness.",
        )
        db.add(ada)
        db.commit()
        db.refresh(ada)

        # Unit 1
        u_ada1 = SyllabusUnit(
            subject_id=ada.id,
            unit_number=1,
            title="Unit I: Algorithms Analysis and Asymptotic Notations",
            description="Growth of functions, Big-O, Omega, Theta notations, Master Theorem for recurrence relations.",
        )
        db.add(u_ada1)
        db.flush()

        t_ada1_1 = SyllabusTopic(
            unit_id=u_ada1.id,
            topic_name="Master Theorem and Recurrence Relations",
            subtopics="Master Theorem cases, Substitution method, Recursion tree method.",
            learning_objectives="Solve recurrences of divide-and-conquer algorithms.",
            importance_level="high",
        )
        db.add(t_ada1_1)

        # Unit 2
        u_ada2 = SyllabusUnit(
            subject_id=ada.id,
            unit_number=2,
            title="Unit II: Divide and Conquer & Dynamic Programming",
            description="Strassen's Matrix Multiplication, 0/1 Knapsack, Longest Common Subsequence (LCS).",
        )
        db.add(u_ada2)
        db.flush()

        t_ada2_1 = SyllabusTopic(
            unit_id=u_ada2.id,
            topic_name="0/1 Knapsack Problem using Dynamic Programming",
            subtopics="Optimal substructure, Tabulation matrix, Backtracking to find selected items.",
            learning_objectives="Formulate DP table and analyze O(nW) complexity.",
            importance_level="high",
        )
        db.add(t_ada2_1)
        db.commit()

        # Paper for ADA Dec 2023
        p_ada23 = QuestionPaper(
            subject_id=ada.id,
            scheme_id=cbgs.id,
            exam_year=2023,
            exam_session=ExamSession.DECEMBER,
            exam_type=ExamType.MAIN,
            source_url="https://www.rgpvonline.com/papers/btech-cs-4-sem-analysis-and-design-of-algorithms-cs-402-dec-2023.pdf",
            total_marks=70,
            verification_status=VerificationStatus.VERIFIED,
            approved_by_id=admin_user.id if admin_user else None,
        )
        db.add(p_ada23)
        db.flush()

        q_ada1 = ExtractedQuestion(
            paper_id=p_ada23.id,
            unit_id=u_ada1.id,
            topic_id=t_ada1_1.id,
            question_number=1,
            sub_question="a",
            question_text="State and explain the Master Theorem for solving recurrence relations. Solve T(n) = 3T(n/4) + n log n.",
            marks=7,
            page_number=1,
            confidence_score=0.99,
            is_human_verified=True,
        )
        q_ada2 = ExtractedQuestion(
            paper_id=p_ada23.id,
            unit_id=u_ada2.id,
            topic_id=t_ada2_1.id,
            question_number=2,
            sub_question="a",
            question_text="Solve the 0/1 Knapsack problem using Dynamic Programming for capacity W = 8 with given weights w = [2, 3, 4, 5] and values v = [3, 4, 5, 8].",
            marks=14,
            page_number=2,
            confidence_score=0.98,
            is_human_verified=True,
        )
        db.add_all([q_ada1, q_ada2])
        db.commit()

    print("Database seeding completed successfully.")
