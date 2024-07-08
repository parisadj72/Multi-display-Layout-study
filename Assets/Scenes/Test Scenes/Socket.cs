using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;

public class Socket : MonoBehaviour
{
    public RawImage LastIcon;
    private XRSocketInteractor socketInteractor;
    /*public string LastIcon
    {
        get { return lastIcon; }
        set { lastIcon = value; }
    }
    void Start()
    {
        IXRSelectInteractable obj = GetComponent<XRSocketInteractor>().firstInteractableSelected;
        if (obj.transform.GetComponent<ViewScript>() != null)
        {
            lastIcon = obj.transform.GetComponent<ViewScript>().Icon;
        }
    }*/
    void Start()
    {
        socketInteractor = GetComponent<XRSocketInteractor>();
    }

    public void OnAttach()
    {
        IXRSelectInteractable obj = socketInteractor.GetOldestInteractableSelected();
        if (obj.transform.GetComponent<ViewScript>() != null)
        {
            LastIcon = obj.transform.GetChild(1).GetChild(0).GetComponent<RawImage>();
            print("socket entered");
        }
    }
}
