import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from exceptions.security_exceptions import token_exception
from service import model_service, auth_service

router = APIRouter(
    prefix="/user_data",
    tags=["user_data"]
)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: str = Depends(oauth2_bearer)):
    user_response = await auth_service.validate_user(token)
    if user_response is None:
        raise token_exception()
    return user_response.id


@router.get("/{user_id}/predict", status_code=status.HTTP_200_OK)
def predict_churn_for_user(user_id: int, current_user: int = Depends(get_current_user)):
    if user_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    model_service.get_or_train_model()

    df = pd.read_csv("resources/csv/user_churn_data.csv")
    df["user_id"] = df["user_id"].astype(int)
    user_data_records = df[df["user_id"] == user_id].to_dict(orient="records")
    if not user_data_records:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_record = user_data_records[0]
    user_features = {k: v for k, v in user_record.items() if k not in ["user_id", "churned"]}
    churn_prediction = model_service.predict_user_churn(user_features)

    return {"user_id": user_id, "churn_prediction": churn_prediction}


@router.get("/performance_metrics/", response_model=dict)
def get_performance_metrics():
    metrics = model_service.get_performance_metrics()
    return metrics


@router.post("/predict_new/", status_code=status.HTTP_200_OK)
def predict_churn_for_new_user(user_features: dict):
    churn_prediction = model_service.predict_user_churn(user_features)
    return {"churn_prediction": churn_prediction}
