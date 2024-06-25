using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit.UI;
using Varjo.XR;
using static UnityEngine.ParticleSystem;

public class View : MonoBehaviour, ISelectHandler
{
    private Toggle toggle;
    private Boolean isOn;
    private Boolean isInteractable;
    public Boolean disabledAtStartup = true;

    private void Awake()
    {
        InitializeView();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
    }

    public Boolean IsOn
    {
        get { return isOn; }
        set { isOn = value; }
    }

    private void InitializeView()
    {
        toggle = GetComponent<Toggle>();
        isInteractable = toggle.interactable;
        IsOn = toggle.isOn;
    }
    public void SetStatus()
    {
        IsOn = toggle.isOn;
    }

    public void TurnOn(Boolean isOn)
    {
        IsOn = isOn;
        toggle.interactable = isOn;
        toggle.isOn = isOn;
        //print("Interaction enabled: " + toggle.interactable);
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }

    public void OnSelect(BaseEventData eventData)
    {
        if (IsOn)
        {
            //print("view clicked. Disable now?");
            StartCoroutine(WaitUntilOff());
        }
    }

    IEnumerator WaitUntilOff()
    {
        yield return new WaitUntil(() => !IsOn);

        //print("view is now off");
        DisableInteraction();
    }
}
