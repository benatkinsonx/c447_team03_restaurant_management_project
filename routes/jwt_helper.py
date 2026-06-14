from flask_jwt_extended import get_jwt, get_jwt_identity 

def get_current_user(): 
    claims = get_jwt() 
    
    return { "user_id": int(get_jwt_identity()), 
            "email": claims.get("email"), 
            "first_name": claims.get("first_name"), 
            "role_id": claims.get("role_id") 
            }
    
def check_admin_access(): 
    claims = get_jwt() 
    
    role_id = str(claims.get("role_id")) 
    
    if role_id not in {"2", "3"}: 
        return """ 
        <h3>Access denied.</h3> 
        <a href="/dashboard"> Back to Dashboard </a> 
        """, 403 
    
    return None

