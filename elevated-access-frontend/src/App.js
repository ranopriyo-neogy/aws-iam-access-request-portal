import './App.css';
import 'bootstrap/dist/css/bootstrap.css';
import { useState , useEffect } from "react";
import { Container, Button, Form  } from "react-bootstrap";
import { Spinner } from 'react-bootstrap';
import API from '@aws-amplify/api';
import Amplify from '@aws-amplify/core';
import aws_exports from './aws-exports';
import { DateTimePickerComponent } from '@syncfusion/ej2-react-calendars';
import moment from "moment";
import axios from 'axios';
import { Typeahead } from 'react-bootstrap-typeahead';
import uilogo from './ui-logo.png';
import {
  AmplifyOauthButton,
  AmplifyAuthenticator
} from "@aws-amplify/ui-react";
Amplify.configure(aws_exports);

function App() {
const minDate = new Date(moment());
const addData = async (formData) => {
    const data = {
      body: formData
    };
    console.log(data)
    await API.post("elevatedaccessapi", "/insert", data);
    setClick(false)
    alert("Request Submitted");
  }
  const initialValues = { account_id:"", user:"", todate:"", policy_arn:"", reason:"", accessType:"" };
  const [formValues, setFormValues] = useState(initialValues);
  const [formErrors, setFormErrors] = useState({});
  const [isSubmit, setIsSubmit] = useState(false);
  const [click, setClick] = useState(false);
  const [optionList,setOptionList] = useState({});
  const [singleSelections, setSingleSelections] = useState([]);
  const [policies, setPolicies] = useState([]);
  const handleChange = (e) => {
    const { id, value } =e.target;
    setFormValues({ ...formValues, [id]: value });
  };
  const handleSubmit = (e) => {                 
    e.preventDefault();
    setFormValues({ ...formValues});
    setFormErrors((validate(formValues)));
    setIsSubmit(true);
  };
  if(singleSelections[0] !== undefined)
  {
    console.log(singleSelections[0])
    formValues['policy_arn'] = singleSelections[0];
    console.log(formValues)
  }

  useEffect(()=>{
    if(Object.keys(formErrors).length === 0 && isSubmit){

      addData(formValues);
      setClick(true);
    }
  }, [formErrors]);

const fetchData = () => {
  axios
    .get('ENTER THE API GATEWAY ENDPOINT TO PULL ALL ACCOUNTS IN AWS ORGANIZATION')
    .then((response) => {
      const { data } = response;
      if(response.status === 200){
        setOptionList(data)
      }else{
      }
    })
    .catch((error) => console.log(error));
};
useEffect(()=>{
  fetchData();
},[])

const fetchPolicies = () => {
  axios
    .get('ENTER THE API GATEWAY ENDPOINT TO PULL ALL ACCOUNTS IN AWS ORGANIZATION')
    .then((response) => {
      const { data } = response;
      if(response.status === 200){
        setPolicies(data)
      }else{
      }
    })
    .catch((error) => console.log(error));
};
useEffect(()=>{
  fetchPolicies();
},[])
  const validate = (values) => {
    const errors = {};
    if(!values.account_id){
      errors.account_id = "Account ID is required"
    }
    if(!values.user){
      errors.user = "User ID is required"
    }
    if(!values.todate){
      errors.todate = "To Date is required"
    }
    if(!values.policy_arn || values.policy_arn === "arn:aws:iam::aws:policy/AdministratorAccess"){
      errors.policy_arn = "Policy is incorrect"
    }
    if(!values.reason){
      errors.reason = "Reason is required"
    }
    if(!values.accessType){
      errors.accessType = "Access Type is required"
    }
    return errors;
  };

  return (
    <AmplifyAuthenticator >
    <AmplifyOauthButton slot="sign-in" />
    <div style={{  display: "block", width: 1000, padding: 100 }}>
    <img src={uilogo} width={160} height={120} alt='Temporary Access Privilege'/>
    <link href="//netdna.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet"/>
    <h1 align="right"> <span class="label label-primary label-sm">Temporary Access Privilege</span></h1>
    &nbsp; 
    <Container>
    <Form onSubmit = {handleSubmit}>
      <Form.Group>
            <Form.Label>AWS Account Name</Form.Label>
            <Form.Control
              as="select"
              className="custom-select"
              id="account_id"
              value={formValues.account_id}  
              onChange={handleChange}
             >
            {Object.entries(optionList).map((selectOption, index) => (
                  <option key={index} value={selectOption[0]}>
                    {selectOption[1]}
                  </option>
                ))}
            </Form.Control>
            <p style={{ color: 'red' }}>{formErrors.account_id}</p>
      </Form.Group>
      <Form.Group>
            <Form.Label>User ID</Form.Label>
            <Form.Control
              as="input"
              className="custom-select"
              id="user"
              value={formValues.user}  
              onChange={handleChange}
             >
            </Form.Control>
            <p style={{ color: 'red' }}>{formErrors.user}</p>
      </Form.Group>
      <Form.Group>
            <Form.Label>Credential Active Till</Form.Label>
            <DateTimePickerComponent id="todate"
            value = {formValues.todate}
            placeholder="Select a date and time"
            onChange={handleChange}
            format="yyyy/MM/dd HH:mm:ss"
            min={minDate}/>
            <p style={{ color: 'red' }}>{formErrors.todate}</p>
      </Form.Group>
      <Form.Group>
        <Form.Label>Policy Arn</Form.Label>
        <Typeahead
          id="policy_arn"
          labelKey="policy_arn"
          onChange={setSingleSelections}
          options={policies}
          placeholder="Choose a policy..."
          value={singleSelections}
        />
        <p style={{ color: 'red' }}>{formErrors.policy_arn}</p>
      </Form.Group>
      <Form.Group>
            <Form.Label>Access Type</Form.Label>
            <Form.Control
              as="select"
              className="custom-select"
              id="accessType"
              value={formValues.accessType}  
              onChange={handleChange}
             >
              <option value="" hidden>Specify access type</option>
              <option value="console">console</option>
              <option value="terminal">terminal</option>
            </Form.Control>
            <p style={{ color: 'red' }}>{formErrors.accessType}</p>
      </Form.Group>
      <Form.Group>
            <Form.Label>Reason</Form.Label>
            <Form.Control
              as="textarea" 
              rows="2" 
              placeholder="Briefly specify the reason for this access"
              id="reason"
              value={formValues.reason}
              onChange={handleChange}
            />
             <p style={{ color: 'red' }}>{formErrors.reason}</p>
      </Form.Group> 
      <Button variant="primary" type="submit">
            {!click && "Submit"}
            {click && <Spinner animation="border" variant="info" />}
      </Button>
    </Form>
    </Container>
  </div>
</AmplifyAuthenticator>
  );
}

export default App;