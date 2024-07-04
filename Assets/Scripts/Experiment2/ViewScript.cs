using System;
using System.Collections;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

public class ViewScript : MonoBehaviour, IPointerClickHandler
{
    public Boolean disabledAtStartup = true;
    private Toggle toggle;
    private float wrongClickCounter = 0;

    public float WrongClickCounter
    {
        get { return wrongClickCounter; }
        set { wrongClickCounter = value; }
    }

    private void Awake()
    {
        toggle = GetComponent<Toggle>();

        if (disabledAtStartup)
        {
            DisableInteraction();
        }
    }

    public void TurnOn()
    {
        toggle.isOn = true;
    }
    public void TurnOff()
    {
        toggle.isOn = false;
    }

    public void DisableInteraction()
    {
        toggle.interactable = false;
    }
    public void EnableInteraction()
    {
        toggle.interactable = true;
    }
    public void OnPointerClick(PointerEventData eventData)
    {
        if (!toggle.interactable)
            wrongClickCounter++;
    }
}
