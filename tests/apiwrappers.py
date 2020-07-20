def sign_person_up(client, name, email=None, description=None):
    obj = {"name": name}
    if email:
        obj["email"] = email
    if description:
        obj["description"] = description
    return client.post("/person/", headers={"X-Token": "coneofsilence"}, json=obj)


def edit_person(client, _id, new_description):
    obj = get_person(client, _id).json()
    obj["description"] = new_description
    return client.put("/person/", headers={"X-Token": "coneofsilence"}, json=obj)


def get_person(client, _id):
    return client.get("/person/{}".format(_id), headers={"X-Token": "coneofsilence"})


def was_person_emailed(client, _id):
    response = get_person(client, _id)
    assert response.status_code == 200
    return response.json()["signup_email_success"]
