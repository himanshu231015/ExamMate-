"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.schemas.common import MessageResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new student or contributor account."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Restrict direct public registration to Student or Contributor only (Admin registration is disabled)
    assigned_role = user_in.role if user_in.role in [UserRole.STUDENT, UserRole.CONTRIBUTOR] else UserRole.STUDENT

    new_user = User(
        email=user_in.email.lower(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=assigned_role,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db=db,
        action="user_registered",
        entity_type="user",
        entity_id=new_user.id,
        user_id=new_user.id,
        details=f"Registered with role {new_user.role.value}",
    )

    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email/ID and password and receive a JWT access token."""
    login_id = credentials.email.strip().lower()

    # Dedicated Admin Credential check: ID = Admin123 (or admin123@rgpvexammate.edu), Password = dj1234
    if login_id in ["admin123", "admin123@rgpvexammate.edu", "admin@rgpvexammate.edu"]:
        if credentials.password != "dj1234" and credentials.password != "Admin@123":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect Admin password. Expected: dj1234",
                headers={"WWW-Authenticate": "Bearer"},
            )

        admin_user = db.query(User).filter(
            (User.email == "admin123@rgpvexammate.edu") | (User.email == "admin@rgpvexammate.edu")
        ).first()

        if not admin_user:
            admin_user = User(
                email="admin123@rgpvexammate.edu",
                hashed_password=hash_password("dj1234"),
                full_name="RGPV Administrator",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
        else:
            # Ensure password hash is updated to dj1234
            if not verify_password("dj1234", admin_user.hashed_password):
                admin_user.hashed_password = hash_password("dj1234")
                db.commit()

        access_token = create_access_token(data={"sub": str(admin_user.id), "role": admin_user.role.value})
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(admin_user),
        )

    # Standard user login check
    user = db.query(User).filter(User.email == login_id).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """Retrieve the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin-only endpoint to list all registered users."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to access user list."
        )
    users = db.query(User).order_by(User.id.asc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.delete("/me", response_model=MessageResponse)
def delete_my_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Allow students to permanently delete their account and associated personal data.
    Enforces privacy rights and data minimization.
    """
    user_id = current_user.id
    log_audit_event(
        db=db,
        action="account_deleted_by_user",
        entity_type="user",
        entity_id=user_id,
        user_id=user_id,
        details="User requested deletion of their account and study data.",
    )
    db.delete(current_user)
    db.commit()

    return MessageResponse(
        message="Your account and associated personal data have been successfully deleted.",
    )
