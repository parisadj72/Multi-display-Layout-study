using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;
using static UnityEngine.ParticleSystem;

public class View : MonoBehaviour, ISelectHandler
{
    private Toggle toggle;
    private Boolean isOn;
    private Boolean hasBeenClicked = false;

    private void Start()
    {
        toggle = GetComponent<Toggle>();
        SetStatus();
        //print("IsOn = " + IsOn);
        //TurnOn(true);
        //DisableInteraction();
        //EventTest();
    }

    public void Awake()
    {
        Start();
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    public Boolean HasBeenClicked
    {
        get { return hasBeenClicked; }
        set { hasBeenClicked = value; }
    }

    public void TurnOn(bool isOn)
    {
        //print("Toggle is: " + toggle.name);
        toggle.isOn = isOn;
        IsOn = isOn;
        toggle.interactable = isOn;
    }

    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void EventTest()
    {
        //print("Event activated");
        SetStatus();
        //print("Window is on? " + IsOn);
    }

    public void OnSelect(BaseEventData eventData)
    {
        if (IsOn && !hasBeenClicked)
        {
            print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
        }
        //print("the view is off...");
        //TurnOff();
        //DisableInteraction();
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        print("view is now off");
        DisableInteraction();
    }

    private void Update()
    {
        if (IsOn && !hasBeenClicked)
        {
            //print("view is still on");
        }
        //print("view is now off");
        //hasBeenClicked = true;
        //DisableInteraction();

    }

    //public void OnDeselect(BaseEventData eventData)
    //{
    //    print("Deselected");
    //}
}
